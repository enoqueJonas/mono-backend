from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from groups.models import (
    Group,
    GroupMember,
    GroupSettings,
    RotationOrder,
)
from groups.services.rotation_service import (
    RotationService,
)


class GroupRotationAPITests(APITestCase):

    def setUp(self):
        self.manager_user = User.objects.create_user(
            phone_number="+258841111111",
            password="password123",
            first_name="Manager",
            last_name="User",
        )

        self.member_user = User.objects.create_user(
            phone_number="+258842222222",
            password="password123",
            first_name="Member",
            last_name="One",
        )

        self.second_member_user = (
            User.objects.create_user(
                phone_number="+258843333333",
                password="password123",
                first_name="Member",
                last_name="Two",
            )
        )

        self.group = Group.objects.create(
            name="Test Group",
            description="Rotation API tests",
        )

        self.settings = GroupSettings.objects.create(
            group=self.group,
            version=1,
            contribution_amount="1000.00",
            currency="MZN",
            contribution_frequency=(
                GroupSettings
                .ContributionFrequency.MONTHLY
            ),
            maximum_members=10,
            rotation_strategy=(
                GroupSettings
                .RotationStrategy.FIXED_ORDER
            ),
            requires_consensus=True,
            allow_manual_contributions=True,
            is_active=True,
        )

        self.manager_membership = (
            GroupMember.objects.create(
                group=self.group,
                user=self.manager_user,
                role=GroupMember.Role.MANAGER,
                status=GroupMember.Status.ACTIVE,
            )
        )

        self.member_membership = (
            GroupMember.objects.create(
                group=self.group,
                user=self.member_user,
                role=GroupMember.Role.MEMBER,
                status=GroupMember.Status.ACTIVE,
            )
        )

        self.second_member_membership = (
            GroupMember.objects.create(
                group=self.group,
                user=self.second_member_user,
                role=GroupMember.Role.MEMBER,
                status=GroupMember.Status.ACTIVE,
            )
        )

        self.url = reverse(
            "group-rotation",
            kwargs={
                "group_id": self.group.id,
            },
        )

    def test_manager_can_generate_rotation(self):
        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.post(
            self.url,
            {
                "cycle_number": 1,
                "contribution_period": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            RotationOrder.objects.filter(
                group=self.group,
                cycle_number=1,
            ).count(),
            3,
        )

        self.assertEqual(
            RotationOrder.objects.filter(
                group=self.group,
                cycle_number=1,
                status=RotationOrder.Status.CURRENT,
            ).count(),
            1,
        )

    def test_regular_member_cannot_generate_rotation(
        self,
    ):
        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.post(
            self.url,
            {
                "cycle_number": 1,
                "contribution_period": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            RotationOrder.objects.filter(
                group=self.group,
                cycle_number=1,
            ).exists()
        )

    def test_active_member_can_list_rotation(self):
        RotationService.generate_cycle(
            group=self.group,
            cycle_number=1,
            contribution_period="2026-09-01",
        )

        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.get(
            self.url,
            {
                "cycle_number": 1,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["data"]),
            3,
        )

    def test_rotation_response_identifies_current_member(
        self,
    ):
        RotationService.generate_cycle(
            group=self.group,
            cycle_number=1,
            contribution_period="2026-09-01",
        )

        self.client.force_authenticate(
            user=self.member_user
        )

        response = self.client.get(
            self.url,
            {
                "cycle_number": 1,
            },
        )

        current = [
            item
            for item in response.data["data"]
            if item["status"]
            == RotationOrder.Status.CURRENT
        ]

        self.assertEqual(
            len(current),
            1,
        )

        self.assertEqual(
            current[0]["position"],
            1,
        )

    def test_cannot_generate_same_cycle_twice(self):
        RotationService.generate_cycle(
            group=self.group,
            cycle_number=1,
            contribution_period="2026-09-01",
        )

        self.client.force_authenticate(
            user=self.manager_user
        )

        response = self.client.post(
            self.url,
            {
                "cycle_number": 1,
                "contribution_period": "2026-09-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            RotationOrder.objects.filter(
                group=self.group,
                cycle_number=1,
            ).count(),
            3,
        )
