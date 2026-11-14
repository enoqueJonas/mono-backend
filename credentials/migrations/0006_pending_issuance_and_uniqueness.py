"""Keep the signed credential durable while a blockchain transaction is pending."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("credentials", "0005_backfill_credential_valid_until")]

    operations = [
        migrations.AlterField(
            model_name="verifiablecredential",
            name="status",
            field=models.CharField(
                max_length=20,
                default="ACTIVE",
                choices=[
                    ("PENDING", "Pending blockchain confirmation"),
                    ("ACTIVE", "Active"),
                    ("REVOKED", "Revoked"),
                ],
            ),
        ),
        migrations.RemoveConstraint(
            model_name="verifiablecredential",
            name="unique_active_vc_member_period",
        ),
        migrations.AddConstraint(
            model_name="verifiablecredential",
            constraint=models.UniqueConstraint(
                fields=["group_member", "credential_type", "period_start", "period_end"],
                condition=models.Q(status__in=["ACTIVE", "PENDING"]),
                name="unique_issuable_vc_member_period",
            ),
        ),
    ]
