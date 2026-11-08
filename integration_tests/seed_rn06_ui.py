"""Seed independent RN06 end-to-end scenarios in throwaway PostgreSQL.

This command has NO payment-provider or blockchain side effects. It must
never be run outside config.settings_integration on disposable test data.
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
    raise RuntimeError("RN06 fixtures are allowed only in an explicit integration-test environment.")
fixture_path = os.environ.get("RN06_E2E_FIXTURE_PATH")
password = os.environ.get("RN06_E2E_PASSWORD")
if not fixture_path or not password or len(password) < 12:
    raise RuntimeError("RN06_E2E_FIXTURE_PATH and a synthetic RN06_E2E_PASSWORD are required.")

identities = {
    "manager": ("+258841990001", "Gestor"),
    "beneficiary": ("+258841990002", "Beneficiario"),
    "voter1": ("+258841990003", "VotanteA"),
    "voter2": ("+258841990004", "VotanteB"),
    "outsider": ("+258841990005", "Externo"),
}
scenario_members = {
    "baseline": ("manager", "beneficiary", "voter1", "voter2"),
    "reversal": ("manager", "beneficiary", "voter1", "voter2"),
    "membership": ("manager", "beneficiary", "voter1", "voter2"),
    "small": ("manager", "beneficiary", "voter1"),
    "legacy": ("manager", "beneficiary", "voter1", "voter2"),
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
    scenario_data = {}
    for scenario, active_identities in scenario_members.items():
        group = Group.objects.create(
            name=f"Xitique RN06 — {scenario}",
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
            requires_consensus=(scenario != "legacy"),
            allow_manual_contributions=True,
            is_active=True,
        )
        members = {}
        for identity in active_identities:
            members[identity] = GroupMember.objects.create(
                group=group,
                user=users[identity],
                role=(
                    GroupMember.Role.MANAGER
                    if identity == "manager" else GroupMember.Role.MEMBER
                ),
                status=GroupMember.Status.ACTIVE,
            )

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
                reference=f"E2E-RN06-{scenario}-{identity}",
            )

        scenario_data[scenario] = {
            "id": str(group.id),
            "memberships": {
                identity: str(member.id)
                for identity, member in members.items()
            },
        }

fixture = {
    "groupId": scenario_data["baseline"]["id"],
    "groups": scenario_data,
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
print("RN06_UI_SEED_CREATED: synthetic identities=5, groups=5, scenarios=baseline/reversal/membership/small/legacy")
