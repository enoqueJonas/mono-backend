from django.core.management.base import BaseCommand

from blockchain.exceptions import (
    CredentialAlreadyAnchored,
)
from blockchain.services.anchor_service import (
    AnchorService,
)
from blockchain.utils.hashing import HashingService


class Command(BaseCommand):
    help = "Anchors a sample credential on the blockchain."

    def handle(
        self,
        *args,
        **options,
    ) -> None:
        document = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1"
            ],
            "type": [
                "VerifiableCredential",
                "SavingsCredential",
            ],
            "issuer": "did:mono:issuer-001",
            "credentialSubject": {
                "id": "did:mono:member-001",
                "status": "ACTIVE",
                "period": "2026-07",
            },
        }

        credential_hash = (
            HashingService.hash_json_hex(
                document
            )
        )

        self.stdout.write(
            f"Credential hash: 0x{credential_hash}"
        )

        service = AnchorService()

        try:
            receipt = service.anchor(document)
        except CredentialAlreadyAnchored:
            self.stdout.write(
                self.style.WARNING(
                    "Credential is already anchored."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "Credential anchored successfully."
            )
        )

        self.stdout.write(
            f"Transaction hash: "
            f"{receipt.transaction_hash}"
        )
        self.stdout.write(
            f"Block number: {receipt.block_number}"
        )
        self.stdout.write(
            f"Block hash: {receipt.block_hash}"
        )
        self.stdout.write(
            f"Wallet: {receipt.wallet_address}"
        )
        self.stdout.write(
            f"Gas used: {receipt.gas_used}"
        )
        self.stdout.write(
            f"Effective gas price: "
            f"{receipt.effective_gas_price}"
        )
        self.stdout.write(
            f"Status: {receipt.status}"
        )
