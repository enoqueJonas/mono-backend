from django.core.management.base import BaseCommand

from blockchain.services.anchor_service import (
    AnchorService,
)


class Command(BaseCommand):

    help = (
        "Calculates the credential hash and "
        "checks if it exists on the blockchain."
    )

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "document",
            type=str,
        )

    def handle(
        self,
        *args,
        **options,
    ):

        service = AnchorService()

        exists = service.credential_exists(
            options["document"]
        )

        self.stdout.write(
            f"Anchored: {exists}"
        )
