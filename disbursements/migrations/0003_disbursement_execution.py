import django.db.models.deletion
import uuid

from django.db import migrations, models

import disbursements.models.execution


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0002_independent_approvals"),
    ]

    operations = [
        migrations.CreateModel(
            name="DisbursementExecution",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("reference", models.CharField(max_length=40, unique=True, default=disbursements.models.execution.new_payout_reference)),
                ("provider", models.CharField(max_length=20, default="MPESA")),
                ("recipient_msisdn", models.CharField(max_length=18)),
                ("amount", models.DecimalField(max_digits=15, decimal_places=2)),
                ("currency", models.CharField(max_length=3)),
                ("status", models.CharField(max_length=32, default="READY", choices=[
                    ("READY", "Ready"),
                    ("INTENT_ANCHORING", "Anchoring approved intent"),
                    ("INTENT_ANCHORED", "Intent anchored"),
                    ("SENDING", "Provider request in flight"),
                    ("PENDING", "Provider pending"),
                    ("UNKNOWN", "Provider status unknown; reconcile only"),
                    ("PROVIDER_CONFIRMED", "Verified by provider"),
                    ("PROVIDER_FAILED", "Rejected by provider"),
                    ("SETTLEMENT_ANCHORING", "Anchoring settlement"),
                    ("SETTLEMENT_ANCHORED", "Settlement anchored"),
                ])),
                ("intent_hash", models.CharField(max_length=64, blank=True, default="")),
                ("intent_anchor_tx", models.CharField(max_length=66, blank=True, default="")),
                ("settlement_hash", models.CharField(max_length=64, blank=True, default="")),
                ("settlement_anchor_tx", models.CharField(max_length=66, blank=True, default="")),
                ("provider_transaction_id", models.CharField(max_length=100, blank=True, default="")),
                ("failure_reason", models.TextField(blank=True, default="")),
                ("initiated_at", models.DateTimeField(null=True, blank=True)),
                ("verified_at", models.DateTimeField(null=True, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("disbursement", models.OneToOneField(
                    to="disbursements.disbursement",
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="execution",
                )),
            ],
        ),
    ]
