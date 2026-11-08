"""Bounded, opt-in contribution anchor reconciliation and health command.

No background scheduler is installed. Running multiple cycles requires an
explicit operator opt-in and PostgreSQL. Never uses real payment APIs.
"""
import os
import time
from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Count
from django.utils import timezone

from contributions.models import ContributionAnchorIntent
from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService


class Command(BaseCommand):
    help = (
        "Reconcile due contribution anchoring intents and report health. "
        "No external payment confirmation is performed."
    )

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument(
            "--cycles", type=int, default=1,
            help="Bounded polling cycles (1 by default; never daemonizes).",
        )
        parser.add_argument(
            "--poll-seconds", type=int, default=30,
            help="Seconds between bounded cycles.",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Read-only status counts; never sign or broadcast anything.",
        )
        parser.add_argument(
            "--fail-on-review", action="store_true",
            help="Exit nonzero if any intent requires manual reconciliation.",
        )

    @staticmethod
    def _snapshot():
        statuses = dict(
            ContributionAnchorIntent.objects.values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )
        total_pending = statuses.get(ContributionAnchorIntent.Status.PENDING, 0)
        total_processing = statuses.get(
            ContributionAnchorIntent.Status.PROCESSING, 0
        )
        total_review = statuses.get(
            ContributionAnchorIntent.Status.REVIEW_REQUIRED, 0
        )
        total_confirmed = statuses.get(
            ContributionAnchorIntent.Status.CONFIRMED, 0
        )
        oldest = ContributionAnchorIntent.objects.filter(
            status=ContributionAnchorIntent.Status.PENDING
        ).order_by("created_at").values_list("created_at", flat=True).first()
        age = int((timezone.now() - oldest).total_seconds()) if oldest else 0
        return {
            "pending": total_pending,
            "processing": total_processing,
            "review": total_review,
            "confirmed": total_confirmed,
            "oldest_pending_seconds": max(0, age),
        }

    def handle(self, *args, **options):
        limit, cycles = options["limit"], options["cycles"]
        interval = options["poll_seconds"]
        if not 1 <= limit <= 1000:
            raise CommandError("--limit must be between 1 and 1000")
        if not 1 <= cycles <= 1440:
            raise CommandError("--cycles must be between 1 and 1440")
        if not 1 <= interval <= 3600:
            raise CommandError("--poll-seconds must be between 1 and 3600")
        if cycles > 1 and (
            os.environ.get("CONTRIBUTION_ANCHOR_WORKER_ENABLED") != "1"
            or connection.vendor != "postgresql"
        ):
            raise CommandError(
                "Multiple cycles require PostgreSQL and explicit "
                "CONTRIBUTION_ANCHOR_WORKER_ENABLED=1 opt-in."
            )

        for cycle in range(1, cycles + 1):
            stats = Counter()
            ids = [] if options["dry_run"] else (
                ContributionAnchorOutboxService.pending_ids(limit=limit)
            )
            for intent_id in ids:
                status = ContributionAnchorOutboxService.process(intent_id)
                stats[status] += 1

            snapshot = self._snapshot()
            self.stdout.write(
                "CONTRIBUTION_ANCHOR_RECOVERY "
                f"cycle={cycle} "
                f"dry_run={int(options['dry_run'])} "
                f"attempted={len(ids)} "
                f"confirmed={stats['CONFIRMED']} "
                f"pending={stats['PENDING']} "
                f"review_required={stats['REVIEW_REQUIRED']} "
                f"processing={stats['PROCESSING']} "
                f"outstanding_pending={snapshot['pending']} "
                f"outstanding_processing={snapshot['processing']} "
                f"outstanding_review={snapshot['review']} "
                f"total_confirmed={snapshot['confirmed']} "
                f"oldest_pending_seconds={snapshot['oldest_pending_seconds']}"
            )
            if options["fail_on_review"] and snapshot["review"]:
                raise CommandError(
                    "Unresolved contribution anchor review requires intervention."
                )

            if cycle < cycles:
                time.sleep(interval)
