"""Post-commit contribution anchor worker.

The durable SQL intent survives a process crash or an RPC outage. An EVM
receipt is recovered by indexed event if mined before local persistence.
This is an on-commit attempt plus explicit retry command, not a job queue.
"""
import logging
from datetime import timedelta
from uuid import uuid4

from django.db import models, transaction
from django.utils import timezone

from blockchain.models import BlockchainAnchorStatus
from blockchain.services.contribution_anchor_service import (
    ContributionAnchorHashMismatch,
    ContributionAnchorService,
)
from contributions.models import ContributionAnchorIntent

logger = logging.getLogger(__name__)


class ContributionAnchorOutboxService:
    LEASE = timedelta(minutes=10)

    @classmethod
    def process(cls, intent_id):
        """Claim in a short SQL transaction, then make the network call."""
        now = timezone.now()
        with transaction.atomic():
            intent = ContributionAnchorIntent.objects.select_for_update().get(pk=intent_id)
            if intent.status in (
                ContributionAnchorIntent.Status.CONFIRMED,
                ContributionAnchorIntent.Status.REVIEW_REQUIRED,
            ):
                return intent.status
            if (
                intent.status == ContributionAnchorIntent.Status.PROCESSING
                and intent.claimed_at is not None
                and intent.claimed_at > now - cls.LEASE
            ):
                return intent.status

            token = uuid4()
            intent.status = ContributionAnchorIntent.Status.PROCESSING
            intent.claim_token = token
            intent.claimed_at = now
            intent.attempt_count += 1
            intent.last_error_code = ""
            intent.save(update_fields=[
                "status", "claim_token", "claimed_at",
                "attempt_count", "last_error_code", "updated_at",
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
                contribution, expected_hash=expected_hash,
            )
            if anchor.status != BlockchainAnchorStatus.CONFIRMED:
                raise ValueError("Contribution anchoring receipt not confirmed.")
        except Exception as exc:
            status = (
                ContributionAnchorIntent.Status.REVIEW_REQUIRED
                if isinstance(exc, ContributionAnchorHashMismatch)
                else ContributionAnchorIntent.Status.PENDING
            )
            with transaction.atomic():
                intent = ContributionAnchorIntent.objects.select_for_update().get(
                    pk=intent_id
                )
                if intent.claim_token == token:
                    intent.status = status
                    intent.claim_token = None
                    intent.claimed_at = None
                    # Never log raw RPC exceptions: may contain sensitive data.
                    intent.last_error_code = type(exc).__name__[:120]
                    intent.save(update_fields=[
                        "status", "claim_token", "claimed_at",
                        "last_error_code", "updated_at",
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
            intent.last_error_code = ""
            intent.save(update_fields=[
                "status", "claim_token", "claimed_at",
                "last_error_code", "updated_at",
            ])
        return ContributionAnchorIntent.Status.CONFIRMED

    @classmethod
    def pending_ids(cls, *, limit=100):
        cutoff = timezone.now() - cls.LEASE
        return list(
            ContributionAnchorIntent.objects.filter(
                models.Q(status=ContributionAnchorIntent.Status.PENDING)
                | models.Q(
                    status=ContributionAnchorIntent.Status.PROCESSING,
                    claimed_at__lte=cutoff,
                )
            ).order_by("created_at").values_list("id", flat=True)[:limit]
        )
