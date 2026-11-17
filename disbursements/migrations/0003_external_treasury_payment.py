import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0002_independent_approvals"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("groups", "0008_alter_rotationorder_contribution_period_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="disbursement",
            name="status",
            field=models.CharField(max_length=30, default="PENDING", choices=[
                ("PENDING", "Pending"),
                ("AWAITING_CONSENSUS", "Awaiting consensus"),
                ("APPROVED", "Approved"),
                ("AWAITING_PAYMENT", "Awaiting external payment"),
                ("AWAITING_CONFIRMATION", "Awaiting beneficiary confirmation"),
                ("DISPUTED", "Payment disputed"),
                ("EVIDENCE_PENDING", "Awaiting on-chain evidence"),
                ("PROCESSING", "Processing"),
                ("COMPLETED", "Completed"),
                ("FAILED", "Failed"),
                ("CANCELLED", "Cancelled"),
            ]),
        ),
        migrations.CreateModel(
            name="TreasuryMandate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=12, choices=[
                    ("MPESA", "M-Pesa"), ("EMOLA", "e-Mola"), ("OTHER", "Other external payment channel")
                ])),
                ("wallet_alias", models.CharField(max_length=64, help_text="Masked/display-only identifier; never a password or API key.")),
                ("appointed_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("group", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="treasury_mandate", to="groups.group")),
                ("custodian", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="custody_mandates", to="groups.groupmember")),
                ("appointed_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="appointed_treasury_mandates", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "external_treasury_mandates"},
        ),
        migrations.CreateModel(
            name="ExternalPaymentReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(max_length=12, choices=[
                    ("MPESA", "M-Pesa"), ("EMOLA", "e-Mola"), ("OTHER", "Other external payment channel")
                ])),
                ("wallet_alias", models.CharField(max_length=64)),
                ("transfer_reference", models.CharField(max_length=100)),
                ("amount", models.DecimalField(max_digits=15, decimal_places=2)),
                ("currency", models.CharField(max_length=3)),
                ("reported_at", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(max_length=12, default="REPORTED", choices=[
                    ("REPORTED", "Reported by custodian"),
                    ("CONFIRMED", "Beneficiary acknowledges receipt"),
                    ("DISPUTED", "Beneficiary disputes receipt"),
                ])),
                ("responded_at", models.DateTimeField(null=True, blank=True)),
                ("dispute_reason", models.TextField(blank=True, default="")),
                ("disbursement", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="external_payment", to="disbursements.disbursement")),
                ("mandate", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payment_reports", to="disbursements.treasurymandate")),
                ("reported_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="external_payments_reported", to=settings.AUTH_USER_MODEL)),
                ("beneficiary_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="external_payments_received", to=settings.AUTH_USER_MODEL)),
                ("confirmed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="external_payments_confirmed", to=settings.AUTH_USER_MODEL)),
            ],
            options={"db_table": "external_payment_reports"},
        ),
        migrations.AddConstraint(
            model_name="externalpaymentreport",
            constraint=models.UniqueConstraint(
                fields=("provider", "transfer_reference"),
                name="unique_external_provider_reference",
            ),
        ),
    ]
