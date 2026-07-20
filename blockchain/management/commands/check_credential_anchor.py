from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from web3 import Web3

from blockchain.clients.credential_registry_client import (
    CredentialRegistryClient,
)
from blockchain.exceptions import BlockchainError


class Command(BaseCommand):
    help = (
        "Checks a credential hash in the "
        "CredentialRegistry contract."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "credential_hash",
            type=str,
            help="Credential hash in 0x-prefixed hexadecimal format.",
        )

    def handle(
        self,
        *args,
        **options,
    ):
        hash_value = options["credential_hash"]

        if not hash_value.startswith("0x"):
            raise CommandError(
                "The credential hash must start with 0x."
            )

        try:
            credential_hash = Web3.to_bytes(
                hexstr=hash_value
            )
        except ValueError as exc:
            raise CommandError(
                "The supplied hash is not valid hexadecimal."
            ) from exc

        try:
            client = CredentialRegistryClient()

            exists = client.credential_exists(
                credential_hash
            )

            self.stdout.write(
                f"Exists: {exists}"
            )

            if not exists:
                return

            credential = client.get_credential(
                credential_hash
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Credential anchor found."
                )
            )

            self.stdout.write(
                f"Revoked: "
                f"{credential['revoked']}"
            )
            self.stdout.write(
                f"Anchored at: "
                f"{credential['anchored_at']}"
            )
            self.stdout.write(
                f"Anchored by: "
                f"{credential['anchored_by']}"
            )

        except BlockchainError as exc:
            raise CommandError(str(exc)) from exc
