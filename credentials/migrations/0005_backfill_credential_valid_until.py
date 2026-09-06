from datetime import timedelta

from django.db import migrations


DEFAULT_VALIDITY_DAYS = 365


def backfill_valid_until(apps, schema_editor):
    VerifiableCredential = apps.get_model(
        "credentials",
        "VerifiableCredential",
    )

    credentials = VerifiableCredential.objects.filter(
        valid_until__isnull=True,
    )

    for credential in credentials.iterator():
        credential.valid_until = (
            credential.valid_from
            + timedelta(days=DEFAULT_VALIDITY_DAYS)
        )
        credential.save(update_fields=["valid_until"])


class Migration(migrations.Migration):

    dependencies = [
        (
            "credentials",
            "0004_remove_blockchainanchor_credentials_credent_c56008_idx_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            backfill_valid_until,
            migrations.RunPython.noop,
        ),
    ]
