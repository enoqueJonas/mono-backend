from django.core.management.base import BaseCommand

from groups.models import Group
from identity.services.did_service import DIDService


class Command(BaseCommand):
    help = "Creates DIDs for groups that do not have one."

    def handle(self, *args, **options):
        groups = Group.objects.filter(
            decentralized_identity__isnull=True
        )

        created_count = 0

        for group in groups.iterator():
            DIDService.create_for_group(group=group)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} group DIDs."
            )
        )
