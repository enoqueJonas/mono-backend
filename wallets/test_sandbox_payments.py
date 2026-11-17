"""Sandbox E2E tests with a deterministic fake chain boundary.

These tests verify application logic and simulated money only. Ganache tests
must separately validate the actual DisbursementRegistry deployment and receipts.
"""
from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import Disbursement
from disbursements.services.disbursement_service import DisbursementService, InvalidDisbursementStatus
from disbursements.services.sandbox_payout_service import SandboxPayoutService, SandboxProofMismatch
from groups.models import Group, GroupMember, GroupSettings, RotationOrder
from wallets.models import SandboxAccount, SandboxEntry, SandboxTransfer
from wallets.services.sandbox_ledger import (
    SandboxInsufficientFunds,
    SandboxLedgerService,
    SandboxTransferConflict,
)


class FakeDisbursementChain:
    def __init__(self):
        self.state = {}
        self.fail_settlement_once = False
        self.authorizations = 0
        self.settlements = 0

    def get(self, key):
        return self.state.setdefault(key, {
            "authorized": False, "settled": False,
            "authorization_hash": "0" * 64, "settlement_hash": "0" * 64,
        }).copy()

    def anchor_authorization(self, *, disbursement_id, authorization_hash):
        item = self.state[disbursement_id]
        assert not item["authorized"]
        item.update(authorized=True, authorization_hash=authorization_hash)
        self.authorizations += 1

    def anchor_verified_settlement(self, *, disbursement_id, settlement_hash):
        if self.fail_settlement_once:
            self.fail_settlement_once = False
            raise RuntimeError("Simulated Ganache outage after fictitious debit")
        item = self.state[disbursement_id]
        assert item["authorized"] and not item["settled"]
        item.update(settled=True, settlement_hash=settlement_hash)
        self.settlements += 1


@override_settings(SANDBOX_PAYMENTS_ENABLED=True)
class SandboxPayoutTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(
                phone_number=f"+25884756000{i}", password="sandbox-pass"
            ) for i in range(4)
        ]
        self.manager, self.beneficiary, self.voter1, self.voter2 = self.users
        self.group = Group.objects.create(name="Grupo sandbox")
        self.settings = GroupSettings.objects.create(
            group=self.group,
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
        self.members = {}
        for user in self.users:
            self.members[user.pk] = GroupMember.objects.create(
                group=self.group, user=user,
                role=(GroupMember.Role.MANAGER if user == self.manager else GroupMember.Role.MEMBER),
                status=GroupMember.Status.ACTIVE,
            )
        self.rotation = RotationOrder.objects.create(
            group=self.group, member=self.members[self.beneficiary.pk],
            group_settings=self.settings, contribution_period=date(2026, 11, 1),
            cycle_number=1, position=1, status=RotationOrder.Status.CURRENT,
        )
        for i, membership in enumerate(self.members.values()):
            contribution = Contribution.objects.create(
                member=membership, group_settings=self.settings,
                amount=Decimal("1000.00"), currency="MZN",
                contribution_period=date(2026, 11, 1),
                status=Contribution.Status.CONFIRMED,
                source=Contribution.Source.MOBILE_WALLET,
                reference=f"SANDBOX-CONTRIBUTION-{i}",
            )
            SandboxLedgerService.record_contribution(contribution)
        self.chain = FakeDisbursementChain()

    def propose_and_approve(self):
        disbursement = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager
        )
        DisbursementService.approve(
            disbursement_id=disbursement.pk, approved_by=self.voter1
        )
        DisbursementService.approve(
            disbursement_id=disbursement.pk, approved_by=self.voter2
        )
        disbursement.refresh_from_db()
        self.assertEqual(disbursement.status, Disbursement.Status.APPROVED)
        return disbursement

    def group_account(self):
        return SandboxAccount.objects.get(
            key=SandboxLedgerService.group_key(self.group.pk, "MZN")
        )

    def test_balance_and_double_entry_for_contributions(self):
        self.assertEqual(self.group_account().balance, Decimal("4000.00"))
        self.assertEqual(SandboxTransfer.objects.count(), 4)
        for transfer in SandboxTransfer.objects.all():
            self.assertEqual(transfer.entries.count(), 2)
            self.assertEqual(
                sum(transfer.entries.values_list("signed_amount", flat=True)),
                Decimal("0.00"),
            )

    def test_contribution_replay_does_not_mint_again(self):
        c = Contribution.objects.get(reference="SANDBOX-CONTRIBUTION-0")
        first = SandboxLedgerService.record_contribution(c)
        again = SandboxLedgerService.record_contribution(c)
        self.assertEqual(first.pk, again.pk)
        self.assertEqual(self.group_account().balance, Decimal("4000.00"))
        self.assertEqual(SandboxTransfer.objects.count(), 4)

    def test_full_virtual_disbursement_and_replay(self):
        d = self.propose_and_approve()
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.complete(disbursement_id=d.pk, completed_by=self.manager)
        result = SandboxPayoutService.execute(
            disbursement_id=d.pk, completed_by=self.manager, client=self.chain
        )
        self.assertEqual(result.status, Disbursement.Status.COMPLETED)
        self.assertEqual(self.group_account().balance, Decimal("0.00"))
        recipient = SandboxAccount.objects.get(
            key=SandboxLedgerService.member_key(self.beneficiary.pk, "MZN")
        )
        self.assertEqual(recipient.balance, Decimal("4000.00"))
        self.assertEqual(self.chain.authorizations, 1)
        self.assertEqual(self.chain.settlements, 1)
        self.assertEqual(SandboxTransfer.objects.filter(purpose="PAYOUT").count(), 1)
        self.assertEqual(
            SandboxPayoutService.execute(
                disbursement_id=d.pk, completed_by=self.manager, client=self.chain
            ).status,
            Disbursement.Status.COMPLETED,
        )
        self.assertEqual(self.chain.authorizations, 1)
        self.assertEqual(self.chain.settlements, 1)
        self.assertEqual(self.group_account().balance, Decimal("0.00"))

    def test_quorum_is_required_before_any_virtual_debit(self):
        d = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager
        )
        with self.assertRaises(InvalidDisbursementStatus):
            SandboxPayoutService.execute(
                disbursement_id=d.pk, completed_by=self.manager, client=self.chain
            )
        self.assertEqual(self.group_account().balance, Decimal("4000.00"))
        self.assertFalse(self.chain.state[str(d.pk)]["authorized"])

    def test_insufficient_virtual_balance_rejects_without_debit(self):
        d = self.propose_and_approve()
        c = Contribution.objects.get(reference="SANDBOX-CONTRIBUTION-0")
        # Move an already recorded simulated credit to a distinct test account
        # to reduce group balance; do not alter actual contribution records.
        group = self.group_account()
        group.balance = Decimal("3000.00")
        group.save(update_fields=["balance"])
        with self.assertRaises(SandboxInsufficientFunds):
            SandboxPayoutService.execute(
                disbursement_id=d.pk, completed_by=self.manager, client=self.chain
            )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)
        self.assertFalse(SandboxTransfer.objects.filter(purpose="PAYOUT").exists())

    def test_chain_outage_after_debit_reconciles_without_second_debit(self):
        d = self.propose_and_approve()
        self.chain.fail_settlement_once = True
        with self.assertRaises(RuntimeError):
            SandboxPayoutService.execute(
                disbursement_id=d.pk, completed_by=self.manager, client=self.chain
            )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.PROCESSING)
        self.assertEqual(self.group_account().balance, Decimal("0.00"))
        self.assertEqual(SandboxTransfer.objects.filter(purpose="PAYOUT").count(), 1)
        repaired = SandboxPayoutService.execute(
            disbursement_id=d.pk, completed_by=self.manager, client=self.chain
        )
        self.assertEqual(repaired.status, Disbursement.Status.COMPLETED)
        self.assertEqual(self.group_account().balance, Decimal("0.00"))
        self.assertEqual(SandboxTransfer.objects.filter(purpose="PAYOUT").count(), 1)

    def test_conflicting_anchor_blocks_virtual_payment(self):
        d = self.propose_and_approve()
        self.chain.state[str(d.pk)] = {
            "authorized": True, "settled": False,
            "authorization_hash": "aa" * 32, "settlement_hash": "0" * 64,
        }
        with self.assertRaises(SandboxProofMismatch):
            SandboxPayoutService.execute(
                disbursement_id=d.pk, completed_by=self.manager, client=self.chain
            )
        self.assertEqual(self.group_account().balance, Decimal("4000.00"))
        self.assertFalse(SandboxTransfer.objects.filter(purpose="PAYOUT").exists())
