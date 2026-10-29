"""Ensure only active managers can trigger a VC on-chain revocation."""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from credentials.models import VerifiableCredential
from groups.models import Group, GroupMember
from identity.models import GroupDID, UserDID
from identity.utils.keys import generate_did_key_pair


@pytest.fixture
def case(db):
    def user(phone):
        return User.objects.create_user(
            phone_number=phone, password="test-only"
        )
    manager = user("+258841000011")
    other = user("+258841000012")
    holder = user("+258841000013")
    group = Group.objects.create(name="Grupo 1")
    other_group = Group.objects.create(name="Grupo 2")
    GroupMember.objects.create(
        user=manager, group=group, role=GroupMember.Role.MANAGER,
        status=GroupMember.Status.ACTIVE,
    )
    GroupMember.objects.create(
        user=other, group=other_group, role=GroupMember.Role.MANAGER,
        status=GroupMember.Status.ACTIVE,
    )
    membership = GroupMember.objects.create(
        user=holder, group=group, role=GroupMember.Role.MEMBER,
        status=GroupMember.Status.ACTIVE,
    )
    issuer_key = generate_did_key_pair()
    holder_key = generate_did_key_pair()
    issuer_did = GroupDID.objects.create(
        group=group, did=issuer_key.did, method=GroupDID.Method.KEY,
        public_key_multibase=issuer_key.public_key_multibase,
        encrypted_private_key=issuer_key.encrypted_private_key,
    )
    holder_did = UserDID.objects.create(
        user=holder, did=holder_key.did, method=UserDID.Method.KEY,
        public_key_multibase=holder_key.public_key_multibase,
        encrypted_private_key=holder_key.encrypted_private_key,
    )
    start = datetime.now(timezone.utc)
    vc = VerifiableCredential.objects.create(
        group_member=membership,
        issued_by=GroupMember.objects.get(group=group,user=manager),
        issuer_did=issuer_did, holder_did=holder_did,
        period_start=date(2026,9,1), period_end=date(2026,9,30),
        valid_from=start, valid_until=start+timedelta(days=365),
        credential_document={"id":str(uuid4())}, credential_hash="a"*64,
    )
    return manager, other, holder, vc


@pytest.mark.django_db
def test_revoke_rejects_unauthenticated_actor_without_blockchain_call(case):
    manager, other, holder, credential = case
    client = APIClient()
    with patch("credentials.application.services.revoke_credential_service.AnchorService") as client_anchor:
        response = client.post(
            f"/api/v1/credentials/{credential.id}/revoke/",
            {"reason":"test"},format="json"
        )
        assert response.status_code == 401
        client_anchor.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("who", ["other", "holder"])
def test_revoke_rejects_unauthorised_group_user(case, who):
    manager, other, holder, credential = case
    client = APIClient()
    client.force_authenticate(user=other if who == "other" else holder)
    with patch("credentials.application.services.revoke_credential_service.AnchorService") as client_anchor:
        response = client.post(
            f"/api/v1/credentials/{credential.id}/revoke/",
            {"reason":"test"},format="json"
        )
        assert response.status_code == 403
        client_anchor.return_value.revoke.assert_not_called()


@pytest.mark.django_db
def test_active_manager_can_revoke(case):
    manager, other, holder, credential = case
    client = APIClient()
    client.force_authenticate(user=manager)
    with patch("credentials.application.services.revoke_credential_service.AnchorService"):
        response = client.post(
            f"/api/v1/credentials/{credential.id}/revoke/",
            {"reason":"audit"},format="json"
        )
    assert response.status_code == 200, response.data
    credential.refresh_from_db()
    assert credential.status == VerifiableCredential.Status.REVOKED
