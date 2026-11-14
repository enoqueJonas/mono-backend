"""Operator-only reconciliation of a durable pending credential."""
from datetime import timedelta
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from credentials.application.services.reconcile_credential_issuance_service import (
    ReconcileCredentialIssuanceService,
    ReconciliationNotReady,
)
from credentials.models import VerifiableCredential


class Command(BaseCommand):
    help = "Finalize a confirmed on-chain credential from a durable pending intent."

    def add_arguments(self, parser):
        parser.add_argument("credential_id", type=UUID)
        parser.add_argument(
            "--force", action="store_true",
            help="Skip five-minute safety age threshold (controlled tests only).",
        )

    def handle(self, *args, **options):
        try:
            record = VerifiableCredential.objects.get(id=options["credential_id"])
        except VerifiableCredential.DoesNotExist as exc:
            raise CommandError("Unknown credential ID.") from exc
        if (
            record.status == VerifiableCredential.Status.PENDING
            and not options["force"]
            and record.created_at > timezone.now() - timedelta(minutes=5)
        ):
            raise CommandError(
                "Credential is too recent. Try again after five minutes."
            )
        try:
            resolved = ReconcileCredentialIssuanceService().reconcile(
                credential_id=options["credential_id"]
            )
        except (ReconciliationNotReady, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Credential {resolved.id}: {resolved.status}"
            )
        )
