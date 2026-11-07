import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="disbursement",
            name="proposed_by",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                blank=True,
                related_name="proposed_disbursements",
            ),
        ),
        migrations.AddField(
            model_name="disbursement",
            name="required_approvals",
            field=models.PositiveIntegerField(default=2),
        ),
        migrations.AddField(
            model_name="disbursement",
            name="eligible_approver_ids",
            field=models.JSONField(default=list),
        ),
        migrations.CreateModel(
            name="DisbursementApproval",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("approved_at", models.DateTimeField(auto_now_add=True)),
                ("approved_by", models.ForeignKey(
                    to=settings.AUTH_USER_MODEL,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="disbursement_approvals",
                )),
                ("disbursement", models.ForeignKey(
                    to="disbursements.disbursement",
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="approvals",
                )),
            ],
            options={"ordering": ["approved_at"]},
        ),
        migrations.AddConstraint(
            model_name="disbursementapproval",
            constraint=models.UniqueConstraint(
                fields=("disbursement", "approved_by"),
                name="unique_disbursement_approval_user",
            ),
        ),
    ]
