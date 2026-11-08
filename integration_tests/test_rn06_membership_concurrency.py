"""PostgreSQL concurrency proof for membership changes touching an RN06 cycle.

Only execute against a disposable PostgreSQL test database with
--ds=config.settings_integration; never against live savings-group data.

The Group row is the shared serialization barrier for service-managed
membership changes and the RN06 proposal/completion checks. Locking individual
ACTIVE members alone is insufficient for new member rows (phantoms).
"""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Event

import pytest
from django.db import connection, transaction
from django.test import TransactionTestCase

from accounts.models import User
from groups.models import Group, GroupMember, GroupSettings
from groups.services.group_service import GroupService


@pytest.mark.django_db(transaction=True)
class RN06MembershipLockingTests(TransactionTestCase):
    def setUp(self):
        assert connection.vendor == "postgresql", (
            "This concurrency test requires PostgreSQL row-level locking"
        )
        self.manager = User.objects.create_user(
            phone_number="+258841886001", password="only-a-synthetic-password"
        )
        self.new_user = User.objects.create_user(
            phone_number="+258841886002", password="only-a-synthetic-password"
        )
        self.departing_user = User.objects.create_user(
            phone_number="+258841886003", password="only-a-synthetic-password"
        )
        self.group = Group.objects.create(name="Xitique RN06 concorrencia SQL")
        self.settings = GroupSettings.objects.create(
            group=self.group, version=1, is_active=True,
            contribution_amount=Decimal("1000.00"), currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=5,
            rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=True, allow_manual_contributions=True,
        )
        GroupMember.objects.create(
            group=self.group, user=self.manager,
            role=GroupMember.Role.MANAGER, status=GroupMember.Status.ACTIVE,
        )
        self.departing = GroupMember.objects.create(
            group=self.group, user=self.departing_user,
            role=GroupMember.Role.MEMBER, status=GroupMember.Status.ACTIVE,
        )

    def _must_wait_for_group_lock(self, operation):
        """Prove a membership write cannot finish while another transaction
        owns the same Group row lock. Use distinct DB connections/threads.
        """
        started, done = Event(), Event()

        def worker():
            from django.db import close_old_connections
            close_old_connections()
            try:
                started.set()
                return operation()
            finally:
                done.set()
                close_old_connections()

        with ThreadPoolExecutor(max_workers=1) as executor:
            with transaction.atomic():
                Group.objects.select_for_update().get(pk=self.group.pk)
                future = executor.submit(worker)
                self.assertTrue(started.wait(timeout=5), "Worker failed to start")
                self.assertFalse(
                    done.wait(timeout=0.6),
                    "Membership operation completed while RN06 group lock was held",
                )
            return future.result(timeout=10)

    def test_join_cannot_insert_member_during_group_ledger_snapshot(self):
        member = self._must_wait_for_group_lock(
            lambda: GroupService.add_member(
                group_id=self.group.pk, added_by=self.manager,
                phone_number=self.new_user.phone_number,
            )
        )
        self.assertEqual(member.user_id, self.new_user.pk)
        self.assertEqual(member.status, GroupMember.Status.ACTIVE)

    def test_leave_cannot_change_membership_during_group_ledger_snapshot(self):
        member = self._must_wait_for_group_lock(
            lambda: GroupService.remove_member(
                group_id=self.group.pk,
                group_member_id=self.departing.pk,
                removed_by=self.manager,
            )
        )
        self.assertEqual(member.status, GroupMember.Status.LEFT)
        self.departing.refresh_from_db()
        self.assertEqual(self.departing.status, GroupMember.Status.LEFT)
