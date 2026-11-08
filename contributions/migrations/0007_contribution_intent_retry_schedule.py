"""Delay retryable contribution RPC failures without busy-looping workers."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("contributions", "0006_contribution_anchor_intent")]

    operations = [
        migrations.AddField(
            model_name="contributionanchorintent",
            name="next_attempt_at",
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text="Earliest time that a bounded retry worker may claim this intent.",
            ),
        ),
        migrations.AddIndex(
            model_name="contributionanchorintent",
            index=models.Index(
                fields=["status", "next_attempt_at"],
                name="contr_anchor_due_idx",
            ),
        ),
    ]
