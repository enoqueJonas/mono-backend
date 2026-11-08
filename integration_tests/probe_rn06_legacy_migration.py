"""Exercise an upgrade of *existing* RN06 records on disposable PostgreSQL.

This migration probe goes beyond makemigrations --check: it creates a
pre-0002 APPROVED record in the old SQL schema, applies 0002, then proves
the legacy record remains untrusted and cannot bypass the quorum.

This is a CI-only test, never a production migration utility.
"""
import os
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

if (
    os.environ.get("RN06_LEGACY_MIGRATION_PROBE") != "1"
    or os.environ.get("DJANGO_SETTINGS_MODULE") != "config.settings_integration"
    or settings.DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql"
    or settings.DATABASES["default"]["NAME"] != "mono_integration"
    or settings.DATABASES["default"]["HOST"] not in ("127.0.0.1", "localhost")
):
    raise RuntimeError("Legacy migration probe is restricted to ephemeral PostgreSQL CI.")

# First ensure all migration prerequisites exist, then restore specifically
# the historical disbursement table shape without the RN06 approval fields.
call_command("migrate", interactive=False, verbosity=0)
call_command("migrate", "disbursements", "0001_initial", interactive=False, verbosity=0)

from accounts.models import User
from groups.models import Group, GroupMember, GroupSettings, RotationOrder

manager = User.objects.create_user(
    phone_number="+258841995001", password="synthetic-only-migration-probe"
)
beneficiary = User.objects.create_user(
    phone_number="+258841995002", password="synthetic-only-migration-probe"
)
group = Group.objects.create(name="LEGACY RN06 migration probe (synthetic)")
group_settings = GroupSettings.objects.create(
    group=group,
    version=1,
    is_active=True,
    contribution_amount=Decimal("1000.00"),
    currency="MZN",
    contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
    maximum_members=4,
    rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
    requires_consensus=False,
    allow_manual_contributions=True,
)
GroupMember.objects.create(
    group=group, user=manager,
    role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
)
beneficiary_membership = GroupMember.objects.create(
    group=group, user=beneficiary,
    role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
)
rotation = RotationOrder.objects.create(
    group=group,
    member=beneficiary_membership,
    group_settings=group_settings,
    contribution_period=date(2026, 11, 1),
    cycle_number=1,
    position=1,
    status=RotationOrder.Status.CURRENT,
)
executor = MigrationExecutor(connection)
historic_state = executor.loader.project_state([("disbursements", "0001_initial")])
LegacyDisbursement = historic_state.apps.get_model("disbursements", "Disbursement")
legacy = LegacyDisbursement.objects.create(
    group_id=group.pk,
    beneficiary_id=beneficiary_membership.pk,
    rotation_order_id=rotation.pk,
    group_settings_id=group_settings.pk,
    cycle_number=1,
    amount=Decimal("2000.00"),
    currency="MZN",
    status="APPROVED",  # Legacy pre-RN06 records could be approved without votes.
)
legacy_id = legacy.pk

# Upgrade the actual SQL schema and inspect the row via current application.
call_command("migrate", "disbursements", "0002_independent_approvals", interactive=False, verbosity=0)

from disbursements.models import Disbursement
from disbursements.services.disbursement_service import (
    DisbursementService,
    InsufficientDisbursementApprovals,
)

upgraded = Disbursement.objects.get(pk=legacy_id)
assert upgraded.status == Disbursement.Status.APPROVED
assert upgraded.proposed_by_id is None
assert upgraded.eligible_approver_ids == []
assert upgraded.required_approvals >= 2
assert upgraded.amount == Decimal("2000.00")

try:
    DisbursementService.complete(
        disbursement_id=upgraded.id,
        completed_by=manager,
    )
except InsufficientDisbursementApprovals:
    pass
else:
    raise AssertionError("Legacy APPROVED disbursement bypassed the independent quorum")

upgraded.refresh_from_db()
rotation.refresh_from_db()
assert upgraded.status == Disbursement.Status.APPROVED
assert rotation.status == RotationOrder.Status.CURRENT
print("RN06_LEGACY_UPGRADE_OK PostgreSQL schema=0001->0002 old_approved_record_untrusted=True rotation_not_advanced=True")
