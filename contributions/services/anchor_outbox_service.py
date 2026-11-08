"""Post-commit contribution anchor worker.

The durable SQL intent survives a process crash or an RPC outage. An EVM
receipt is recovered by indexed event if mined before local persistence.
This is an on-commit attempt plus explicit retry command, not a job queue.
"""
import logging
from contextlib import contextmanager
from hashlib import sha256
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.db import connection, models, transaction
from django.utils import timezone

from blockchain.models import BlockchainAnchorStatus
from blockchain.services.contribution_anchor_service import (
    ContributionAnchorHashMismatch,
    ContributionAnchorSubmissionUncertain,
    ContributionAnchorService,
)
from contributions.models import ContributionAnchorIntent

logger = logging.getLogger(__name__)


class ContributionAnchorOutboxService:
    LEASE = timedelta(minutes=10)
    MAX_ATTEMPTS = 6

    @staticmethod
    @contextmanager
    def _operator_lock():
        """One live signer per configured chain and operator.

        A PostgreSQL *session* advisory lock (not a row or transaction lock)
        serializes chain reads and signing across Django worker processes.
        The lock is held during RPC, but no Group row or SQL transaction is.
        SQLite unit tests exercise state transitions without this guarantee.
        """
        if connection.vendor != "postgresql":
            yield True
            return
        if connection.in_atomic_block:
            raise RuntimeError("Signer lock cannot run inside an SQL transaction.")
        identity = (
            f"mono:contribution-signer:{settings.BLOCKCHAIN_CHAIN_ID}:"
            f"{settings.BLOCKCHAIN_ACCOUNT_ADDRESS.lower()}"
        )
        key = int.from_bytes(
            sha256(identity.encode("utf-8")).digest()[:8],
            byteorder="big",
            signed=True,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(%s)", [key])
            acquired = bool(cursor.fetchone()[0])
        try:
            yield acquired
        finally:
            if acquired:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_unlock(%s)", [key])
                    if not cursor.fetchone()[0]:
                        raise RuntimeError("Failed to release EVM operator advisory lock.")

    @staticmethod
    def _retry_delay(attempt_count):
        # 15 seconds, 30, 60 ... capped at one hour.
        return timedelta(seconds=min(3600, 15 * 2 ** min(max(attempt_count - 1, 0), 8)))

    @classmethod
    def process(cls, intent_id, *, reconcile_only=False):
        with cls._operator_lock() as acquired:
            if not acquired:
                # A different worker owns the signer. Leave this intent
                # unchanged and let the bounded polling worker revisit it.
                return ContributionAnchorIntent.objects.only("status").get(
                    pk=intent_id
                ).status
            return cls._process_with_signer_lock(
                intent_id, reconcile_only=reconcile_only,
            )

    @classmethod
    def _process_with_signer_lock(cls, intent_id, *, reconcile_only=False):
        """Claim in a short SQL transaction, then make the network call."""
        now = timezone.now()
        with transaction.atomic():
            intent = ContributionAnchorIntent.objects.select_for_update().get(pk=intent_id)
            if intent.status == ContributionAnchorIntent.Status.CONFIRMED:
                return intent.status
            if (
                intent.status == ContributionAnchorIntent.Status.REVIEW_REQUIRED
                and not reconcile_only
            ):
                return intent.status
            if (
                intent.status == ContributionAnchorIntent.Status.PROCESSING
                and intent.claimed_at is not None
                and intent.claimed_at > now - cls.LEASE
            ):
                return intent.status

            # A worker that died while PROCESSING may have broadcast
            # already; stale leases must inspect chain state but NOT send.
            stale_processing = (
                reconcile_only
                or intent.status in (
                    ContributionAnchorIntent.Status.PROCESSING,
                    ContributionAnchorIntent.Status.REVIEW_REQUIRED,
                )
            )
            token = uuid4()
            intent.status = ContributionAnchorIntent.Status.PROCESSING
            intent.claim_token = token
            intent.claimed_at = now
            intent.attempt_count += 1
            intent.next_attempt_at = None
            intent.last_error_code = ""
            intent.save(update_fields=[
                "status", "claim_token", "claimed_at",
                "attempt_count", "next_attempt_at",
                "last_error_code", "updated_at",
            ])
            contribution_id = intent.contribution_id
            expected_hash = intent.content_hash

        # RPC occurs outside the Group lock and outside SQL atomic blocks.
        try:
            contribution = ContributionAnchorIntent.objects.select_related(
                "contribution", "contribution__member",
                "contribution__group_settings",
            ).get(pk=intent_id).contribution
            anchor = ContributionAnchorService().anchor(
                contribution,
                expected_hash=expected_hash,
                allow_submit=not stale_processing,
            )
            if anchor.status != BlockchainAnchorStatus.CONFIRMED:
                raise ValueError("Contribution anchoring receipt not confirmed.")
        except Exception as exc:
            status = (
                ContributionAnchorIntent.Status.REVIEW_REQUIRED
                if isinstance(
                    exc,
                    (ContributionAnchorHashMismatch, ContributionAnchorSubmissionUncertain),
                )
                else ContributionAnchorIntent.Status.PENDING
            )
            with transaction.atomic():
                intent = ContributionAnchorIntent.objects.select_for_update().get(
                    pk=intent_id
                )
                if intent.claim_token == token:
                    if (
                        status == ContributionAnchorIntent.Status.PENDING
                        and intent.attempt_count >= cls.MAX_ATTEMPTS
                    ):
                        # Exhausted bounded retries require operator review;
                        # never spin forever against a failing provider.
                        status = ContributionAnchorIntent.Status.REVIEW_REQUIRED
                    intent.status = status
                    intent.claim_token = None
                    intent.claimed_at = None
                    intent.next_attempt_at = (
                        timezone.now() + cls._retry_delay(intent.attempt_count)
                        if status == ContributionAnchorIntent.Status.PENDING
                        else None
                    )
                    # Never log raw RPC exceptions: may contain sensitive data.
                    intent.last_error_code = type(exc).__name__[:120]
                    intent.save(update_fields=[
                        "status", "claim_token", "claimed_at",
                        "next_attempt_at", "last_error_code", "updated_at",
                    ])
            logger.warning(
                "Contribution anchoring deferred; contribution=%s error_type=%s",
                contribution_id, type(exc).__name__,
            )
            return status

        with transaction.atomic():
            intent = ContributionAnchorIntent.objects.select_for_update().get(
                pk=intent_id
            )
            # A slow first attempt may have had its lease reclaimed. The next
            # worker will observe and recover the already-mined event.
            if intent.claim_token != token:
                return intent.status
            intent.status = ContributionAnchorIntent.Status.CONFIRMED
            intent.claim_token = None
            intent.claimed_at = None
            intent.next_attempt_at = None
            intent.last_error_code = ""
            intent.save(update_fields=[
                "status", "claim_token", "claimed_at",
                "next_attempt_at", "last_error_code", "updated_at",
            ])
        return ContributionAnchorIntent.Status.CONFIRMED

    @classmethod
    def pending_ids(cls, *, limit=100):
        now = timezone.now()
        cutoff = now - cls.LEASE
        due = (
            models.Q(next_attempt_at__isnull=True)
            | models.Q(next_attempt_at__lte=now)
        )
        return list(
            ContributionAnchorIntent.objects.filter(
                (models.Q(status=ContributionAnchorIntent.Status.PENDING) & due)
                | models.Q(
                    status=ContributionAnchorIntent.Status.PROCESSING,
                    claimed_at__lte=cutoff,
                )
            ).order_by("created_at").values_list("id", flat=True)[:limit]
        )
