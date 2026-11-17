# Sandbox ledger: all balances represent fictitious money in a test system.
import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="SandboxAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=110, unique=True)),
                ("role", models.CharField(max_length=12, choices=[("ISSUER", "Test-money issuer"), ("GROUP", "Xitique test account"), ("MEMBER", "Member test account")])),
                ("currency", models.CharField(default="MZN", max_length=3)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
            ],
            options={"db_table": "sandbox_accounts"},
        ),
        migrations.CreateModel(
            name="SandboxTransfer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("idempotency_key", models.CharField(max_length=130, unique=True)),
                ("purpose", models.CharField(max_length=16, choices=[("CONTRIBUTION", "Simulated contribution receipt"), ("PAYOUT", "Simulated disbursement")])),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("currency", models.CharField(max_length=3)),
                ("reference", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sandbox_debits", to="wallets.sandboxaccount")),
                ("destination", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sandbox_credits", to="wallets.sandboxaccount")),
            ],
            options={"db_table": "sandbox_transfers"},
        ),
        migrations.CreateModel(
            name="SandboxEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("signed_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sandbox_entries", to="wallets.sandboxaccount")),
                ("transfer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="entries", to="wallets.sandboxtransfer")),
            ],
            options={"db_table": "sandbox_entries"},
        ),
        migrations.AddConstraint(
            model_name="sandboxentry",
            constraint=models.UniqueConstraint(
                fields=("transfer", "account"), name="unique_sandbox_transfer_account"
            ),
        ),
    ]
