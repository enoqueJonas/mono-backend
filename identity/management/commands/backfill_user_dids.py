from django.core.management.base import BaseCommand

from accounts.models import User
from identity.services.did_service import DIDService


class Command(BaseCommand):
    help = "Creates DIDs for users that do not have one."

    def handle(self, *args, **options):
        users = User.objects.filter(
            decentralized_identity__isnull=True
        )

        created_count = 0

        for user in users.iterator():
            DIDService.create_for_user(user=user)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} user DIDs."
            )
        )
