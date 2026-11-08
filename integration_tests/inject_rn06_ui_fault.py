"""Inject an explicit failure into the synthetic RN06 E2E PostgreSQL fixture.

This is intentionally NOT an HTTP endpoint or application functionality.
The subprocess is invoked by the CI runner only after two real browser votes.
"""
import json
import os
from pathlib import Path

from django.conf import settings
from django.db import transaction

from contributions.models import Contribution

if (
    os.environ.get("RN06_LIVE_E2E_SEED") != "1"
    or os.environ.get("DJANGO_SETTINGS_MODULE") != "config.settings_integration"
    or settings.DATABASES["default"]["NAME"] != "mono_integration"
    or os.environ.get("RN06_E2E_FAULT_SCENARIO") != "reversal"
):
    raise RuntimeError("Refusing fault injection outside RN06 disposable integration database.")

fixture_path = os.environ.get("RN06_E2E_FIXTURE_PATH")
if not fixture_path:
    raise RuntimeError("Missing RN06_E2E_FIXTURE_PATH")
fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
scenario = fixture["groups"]["reversal"]
target_member_id = scenario["memberships"]["voter1"]

with transaction.atomic():
    contribution = Contribution.objects.select_for_update().get(
        member_id=target_member_id,
        reference="E2E-RN06-reversal-voter1",
        status=Contribution.Status.CONFIRMED,
    )
    contribution.status = Contribution.Status.REVERSED
    contribution.save(update_fields=["status", "updated_at"])
print("RN06_FAULT_INJECTED reversal_of_synthetic_contribution=True")
