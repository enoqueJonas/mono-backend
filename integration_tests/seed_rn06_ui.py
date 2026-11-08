"""Seed a throwaway PostgreSQL database for the *real* RN06 browser E2E test.

Invoked only by the paired frontend CI:
  RN06_LIVE_E2E_SEED=1 DJANGO_SETTINGS_MODULE=config.settings_integration \
  RN06_E2E_FIXTURE_PATH=/path/to/fixture.json \
  RN06_E2E_PASSWORD='synthetic-local-password' \
  python manage.py shell -c 'exec(open("integration_tests/seed_rn06_ui.py").read())'

Never run against a production database. Creates simulated contributions only;
does not execute payments, emit DIDs or anchor blockchain transactions.
"""
import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

from django.db import transaction

from accounts.models import User
from contributions.models import Contribution
from groups.models import Group, GroupMember, GroupSettings, RotationOrder


if (
    os.environ.get("RN06_LIVE_E2E_SEED") != "1"
    or os.environ.get("DJANGO_SETTINGS_MODULE") != "config.settings_integration"
):
    raise RuntimeError(
        "RN06 UI seeding is permitted only with the explicit integration-test guard."
    )
fixture_path = os.environ.get("RN06_E2E_FIXTURE_PATH")
password = os.environ.get("RN06_E2E_PASSWORD")
if not fixture_path or not password or len(password) < 12:
    raise RuntimeError("Set RN06_E2E_FIXTURE_PATH and a synthetic RN06_E2E_PASSWORD.")

identities = {
    "manager": ("+258841990001", "Gestor"),
    "beneficiary": ("+258841990002", "Beneficiario"),
    "voter1": ("+258841990003", "VotanteA"),
    "voter2": ("+258841990004", "VotanteB"),
    "outsider": ("+258841990005", "Externo"),
}

with transaction.atomic():
    users = {
        key: User.objects.create_user(
            phone_number=phone,
            password=password,
            first_name=given_name,
            last_name="RN06Teste",
        )
        for key, (phone, given_name) in identities.items()
    }
    group = Group.objects.create(
        name="Xitique RN06 — ensaio automatizado",
        description="Dados ficticios, nunca usados para pagamentos reais",
    )
    group_settings = GroupSettings.objects.create(
        group=group,
        version=1,
        contribution_amount=Decimal("1000.00"),
        currency="MZN",
        contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
        maximum_members=5,
        rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
        requires_consensus=True,
        allow_manual_contributions=True,
        is_active=True,
    )
    members = {}
    for identity in ("manager", "beneficiary", "voter1", "voter2"):
        membership = GroupMember.objects.create(
            group=group,
            user=users[identity],
            role=(
                GroupMember.Role.MANAGER
                if identity == "manager" else GroupMember.Role.MEMBER
            ),
            status=GroupMember.Status.ACTIVE,
        )
        members[identity] = membership

    period = date(2026, 11, 1)
    RotationOrder.objects.create(
        group=group,
        member=members["beneficiary"],
        group_settings=group_settings,
        contribution_period=period,
        cycle_number=1,
        position=1,
        status=RotationOrder.Status.CURRENT,
    )
    for identity, member in members.items():
        Contribution.objects.create(
            member=member,
            group_settings=group_settings,
            amount=Decimal("1000.00"),
            currency="MZN",
            contribution_period=period,
            source=Contribution.Source.MANUAL,
            status=Contribution.Status.CONFIRMED,
            reference=f"E2E-RN06-{identity}",
        )

fixture = {
    "groupId": str(group.id),
    "users": {
        name: {"id": str(user.id), "phone": user.phone_number}
        for name, user in users.items()
    },
    "cycleNumber": 1,
    "requiredApprovals": 2,
    "expectedAmount": "4000.00",
}
Path(fixture_path).write_text(
    json.dumps(fixture, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("RN06_UI_SEED_CREATED: synthetic identities=5, active members=4, cycles=1")
