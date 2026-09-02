from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from groups.models import GroupSettings
from accounts.models import User
from groups.models import (
    Group,
    GroupMember,
)
from penalties.models import Penalty
from penalties.services import (
    InactivePenaltyMember,
    PenaltyAlreadyResolved,
    PenaltyReasonRequired,
    PenaltyService,
)


class PenaltyServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+258846666666",
            password="test1234",
        )

        self.group = Group.objects.create(
            name="Grupo Penalidades",
        )

        self.member = GroupMember.objects.create(
            group=self.group,
            user=self.user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

    def test_create_penalty_for_active_member(self):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        self.assertEqual(
            penalty.member,
            self.member,
        )

        self.assertEqual(
            penalty.reason,
            "Late contribution.",
        )

        self.assertEqual(
            penalty.status,
            Penalty.Status.ACTIVE,
        )

    def test_cannot_create_penalty_without_reason(self):
        with self.assertRaises(
            PenaltyReasonRequired
        ):
            PenaltyService.create(
                member=self.member,
                reason="",
            )

    def test_cannot_create_penalty_for_inactive_member(
        self,
    ):
        self.member.status = (
            GroupMember.Status.SUSPENDED
        )

        self.member.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        with self.assertRaises(
            InactivePenaltyMember
        ):
            PenaltyService.create(
                member=self.member,
                reason="Late contribution.",
            )

    def test_resolve_penalty_preserves_record(self):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        PenaltyService.resolve(
            penalty_id=penalty.id,
        )

        penalty.refresh_from_db()

        self.assertEqual(
            penalty.status,
            Penalty.Status.RESOLVED,
        )

        self.assertIsNotNone(
            penalty.resolved_at,
        )

        self.assertTrue(
            Penalty.objects.filter(
                id=penalty.id
            ).exists()
        )

    def test_cannot_resolve_penalty_twice(self):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        PenaltyService.resolve(
            penalty_id=penalty.id,
        )

        with self.assertRaises(
            PenaltyAlreadyResolved
        ):
            PenaltyService.resolve(
                penalty_id=penalty.id,
            )

    def test_has_active_penalty(self):
        PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        self.assertTrue(
            PenaltyService.has_active_penalty(
                member=self.member,
            )
        )

    def test_resolved_penalty_is_not_active(self):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        PenaltyService.resolve(
            penalty_id=penalty.id,
        )

        self.assertFalse(
            PenaltyService.has_active_penalty(
                member=self.member,
            )
        )


class PenaltyAPITests(APITestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(
            phone_number="+258847777777",
            password="test1234",
        )

        self.member_user = User.objects.create_user(
            phone_number="+258848888888",
            password="test1234",
        )

        self.outsider_user = User.objects.create_user(
            phone_number="+258849999999",
            password="test1234",
        )

        self.group = Group.objects.create(
            name="Grupo Penalidades API",
        )

        self.manager = GroupMember.objects.create(
            group=self.group,
            user=self.manager_user,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        )

        self.member = GroupMember.objects.create(
            group=self.group,
            user=self.member_user,
            role=GroupMember.Role.MEMBER,
            status=GroupMember.Status.ACTIVE,
        )

        self.other_group = Group.objects.create(
            name="Outro Grupo",
        )

        self.outsider_member = (
            GroupMember.objects.create(
                group=self.other_group,
                user=self.outsider_user,
                role=GroupMember.Role.MEMBER,
                status=GroupMember.Status.ACTIVE,
            )
        )

        self.list_url = reverse(
            "group-penalty-list-create",
            kwargs={
                "group_id": self.group.id,
            },
        )

    def test_manager_can_create_penalty(self):
        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.post(
            self.list_url,
            {
                "member_id": str(self.member.id),
                "reason": "Late contribution.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        penalty = Penalty.objects.get(
            member=self.member
        )

        self.assertEqual(
            penalty.reason,
            "Late contribution.",
        )

        self.assertEqual(
            penalty.status,
            Penalty.Status.ACTIVE,
        )

    def test_regular_member_cannot_create_penalty(self):
        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.post(
            self.list_url,
            {
                "member_id": str(self.member.id),
                "reason": "Late contribution.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Penalty.objects.filter(
                member=self.member,
            ).exists()
        )

    def test_cannot_penalize_member_from_another_group(
        self,
    ):
        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.post(
            self.list_url,
            {
                "member_id": str(
                    self.outsider_member.id
                ),
                "reason": "Late contribution.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Penalty.objects.filter(
                member=self.outsider_member,
            ).exists()
        )

    def test_active_member_can_list_group_penalties(
        self,
    ):
        PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["data"]),
            1,
        )

        self.assertEqual(
            response.data["data"][0]["reason"],
            "Late contribution.",
        )

    def test_manager_can_resolve_penalty(self):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        self.client.force_authenticate(
            user=self.manager_user
        )

        url = reverse(
            "group-penalty-resolve",
            kwargs={
                "group_id": self.group.id,
                "penalty_id": penalty.id,
            },
        )

        response = self.client.post(
            url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        penalty.refresh_from_db()

        self.assertEqual(
            penalty.status,
            Penalty.Status.RESOLVED,
        )

        self.assertIsNotNone(
            penalty.resolved_at
        )

    def test_regular_member_cannot_resolve_penalty(
        self,
    ):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        self.client.force_authenticate(
            user=self.member_user
        )

        url = reverse(
            "group-penalty-resolve",
            kwargs={
                "group_id": self.group.id,
                "penalty_id": penalty.id,
            },
        )

        response = self.client.post(
            url,
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        penalty.refresh_from_db()

        self.assertEqual(
            penalty.status,
            Penalty.Status.ACTIVE,
        )

    def test_resolved_penalty_remains_in_history(
        self,
    ):
        penalty = PenaltyService.create(
            member=self.member,
            reason="Late contribution.",
        )

        PenaltyService.resolve(
            penalty_id=penalty.id,
        )

        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["data"]),
            1,
        )

        self.assertEqual(
            response.data["data"][0]["status"],
            Penalty.Status.RESOLVED,
        )

        self.assertEqual(
            response.data["data"][0]["id"],
            str(penalty.id),
        )
