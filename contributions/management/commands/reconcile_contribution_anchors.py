"""Explicit retry/recovery of durable contribution EVM anchoring intents."""
from collections import Counter

from django.core.management.base import BaseCommand, CommandError

from contributions.services.anchor_outbox_service import ContributionAnchorOutboxService


class Command(BaseCommand):
    help = (
        "Retry pending or expired contribution anchoring intents. "
        "This NEVER confirms that an external payment occurred."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=100,
            help="Maximum number of intents to process in this run.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        if not 1 <= limit <= 1000:
            raise CommandError("--limit must be between 1 and 1000")

        ids = ContributionAnchorOutboxService.pending_ids(limit=limit)
        stats = Counter()
        for intent_id in ids:
            status = ContributionAnchorOutboxService.process(intent_id)
            stats[status] += 1

        self.stdout.write(
            "CONTRIBUTION_ANCHOR_RECOVERY "
            f"attempted={len(ids)} "
            f"confirmed={stats['CONFIRMED']} "
            f"pending={stats['PENDING']} "
            f"review_required={stats['REVIEW_REQUIRED']} "
            f"processing={stats['PROCESSING']}"
        )
        if stats["REVIEW_REQUIRED"]:
            raise CommandError(
                "One or more contribution hashes require manual review."
            )
