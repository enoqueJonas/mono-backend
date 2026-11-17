import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0002_independent_approvals"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="disbursement",
            name="external_transfer_reference",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="disbursement",
            name="transfer_declared_by",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.PROTECT,
                null=True, blank=True,
                related_name="declared_disbursement_transfers",
            ),
        ),
        migrations.AddConstraint(
            model_name="disbursement",
            constraint=models.UniqueConstraint(
                fields=("group", "external_transfer_reference"),
                condition=Q(external_transfer_reference__isnull=False),
                name="unique_group_external_transfer_ref",
            ),
        ),
    ]
