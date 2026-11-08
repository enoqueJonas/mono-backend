# New intent persists before external RPC; avoids keeping Group locks during IO.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contributions", "0005_alter_contribution_group_settings"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContributionAnchorIntent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content_hash", models.CharField(max_length=64)),
                ("status", models.CharField(
                    max_length=20,
                    choices=[
                        ("PENDING", "Awaiting anchor or retry"),
                        ("PROCESSING", "Worker has claimed the attempt"),
                        ("CONFIRMED", "Reconciled on chain and in SQL"),
                        ("REVIEW_REQUIRED", "Hash or ledger mismatch"),
                    ],
                    default="PENDING",
                )),
                ("attempt_count", models.PositiveIntegerField(default=0)),
                ("claimed_at", models.DateTimeField(blank=True, null=True)),
                ("claim_token", models.UUIDField(blank=True, null=True)),
                ("last_error_code", models.CharField(blank=True, default="", max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("contribution", models.OneToOneField(
                    to="contributions.contribution",
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="anchor_intent",
                )),
            ],
            options={
                "db_table": "contribution_anchor_intents",
                "indexes": [models.Index(fields=["status", "created_at"], name="contr_anchor_status_idx")],
            },
        ),
    ]
