"""Non-custodial wallet designation and report/confirmation evidence."""
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0002_independent_approvals"),
        ("groups", "0008_alter_rotationorder_contribution_period_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalWalletCustody",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=20)),
                ("wallet_number", models.CharField(max_length=32)),
                ("designated_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("custodian", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="external_wallet_custodies", to="groups.groupmember",
                )),
                ("designated_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="designated_external_wallets", to=settings.AUTH_USER_MODEL,
                )),
                ("group", models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="external_wallet_custody", to="groups.group",
                )),
            ],
            options={"db_table": "external_wallet_custody"},
        ),
        migrations.CreateModel(
            name="ExternalPaymentReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=20)),
                ("reference", models.CharField(max_length=120)),
                ("recipient_wallet_number", models.CharField(max_length=32)),
                ("amount", models.DecimalField(max_digits=15, decimal_places=2)),
                ("currency", models.CharField(max_length=3)),
                ("status", models.CharField(
                    max_length=20,
                    choices=[
                        ("REPORTED", "Reported by custodian"),
                        ("CONFIRMED", "Confirmed by beneficiary"),
                        ("DISPUTED", "Disputed by beneficiary"),
                    ],
                    default="REPORTED",
                )),
                ("reported_at", models.DateTimeField(auto_now_add=True)),
                ("confirmed_at", models.DateTimeField(blank=True, null=True)),
                ("disputed_at", models.DateTimeField(blank=True, null=True)),
                ("dispute_reason", models.TextField(blank=True, default="")),
                ("confirmed_by", models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                    related_name="confirmed_external_payment_receipts",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("reported_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="reported_external_payments",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("disbursement", models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="external_payment_report", to="disbursements.disbursement",
                )),
            ],
            options={"db_table": "external_payment_reports"},
        ),
        migrations.AddConstraint(
            model_name="externalpaymentreport",
            constraint=models.UniqueConstraint(
                fields=("provider", "reference"),
                name="unique_external_provider_reference",
            ),
        ),
        migrations.AddField(
            model_name="disbursement", name="custodian_at_proposal",
            field=models.ForeignKey(
                to="groups.groupmember", on_delete=django.db.models.deletion.PROTECT,
                related_name="custodied_disbursement_proposals",
                null=True, blank=True,
            ),
        ),
        migrations.AddField(
            model_name="disbursement", name="custody_provider_at_proposal",
            field=models.CharField(max_length=20, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="disbursement", name="custody_wallet_at_proposal",
            field=models.CharField(max_length=32, blank=True, default=""),
        ),
    ]
