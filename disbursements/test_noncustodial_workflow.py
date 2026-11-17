from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import (
    Disbursement, ExternalPaymentReport, TreasuryMandate,
)
from disbursements.services.disbursement_service import (
    DisbursementService, InvalidDisbursementStatus,
)
from disbursements.services.noncustodial_service import (
    ExternalEvidenceMismatch, InvalidCustodian,
    NonCustodialDisbursementService as Service,
    RepeatedPaymentReport, UnauthorizedReceiptResponse,
)
from groups.models import Group, GroupMember, GroupSettings, RotationOrder


class FakeEvidenceChain:
    def __init__(self):
        self.authorization = {}
        self.ack = {}
        self.authorization_count = 0
        self.ack_count = 0
        self.fail_after_ack_once = False

    def get(self, disbursement_id):
        h = self.authorization.get(disbursement_id)
        return {"authorized": h is not None, "authorization_hash": h or ("00" * 32)}

    def anchor_authorization(self, *, disbursement_id, authorization_hash):
        assert disbursement_id not in self.authorization
        self.authorization[disbursement_id] = authorization_hash
        self.authorization_count += 1

    def get_beneficiary_acknowledgment(self, disbursement_id):
        h = self.ack.get(disbursement_id)
        return {"exists": h is not None, "evidence_hash": h or ("00" * 32)}

    def anchor_beneficiary_acknowledgment(self, *, disbursement_id, evidence_hash):
        assert disbursement_id in self.authorization
        assert disbursement_id not in self.ack
        self.ack[disbursement_id] = evidence_hash
        self.ack_count += 1
        if self.fail_after_ack_once:
            self.fail_after_ack_once = False
            raise TimeoutError("EVM mined, simulated response lost")


@override_settings(NON_CUSTODIAL_DISBURSEMENTS_ENABLED=True, SANDBOX_PAYMENTS_ENABLED=True)
class ExternalDisbursementWorkflowTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(phone_number=f"+25884765000{i}", password="test-only")
            for i in range(5)
        ]
        self.manager, self.beneficiary, self.treasurer, self.voter2, self.outsider = self.users
        self.group = Group.objects.create(name="Xitique non custodial")
        self.settings = GroupSettings.objects.create(
            group=self.group, version=1, is_active=True,
            contribution_amount=Decimal("1000.00"), currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=5,
            rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=True, allow_manual_contributions=True,
        )
        self.members = {}
        for user, role in [
            (self.manager, GroupMember.Role.MANAGER),
            (self.beneficiary, GroupMember.Role.MEMBER),
            (self.treasurer, GroupMember.Role.TREASURER),
            (self.voter2, GroupMember.Role.MEMBER),
        ]:
            self.members[user.pk] = GroupMember.objects.create(
                group=self.group, user=user,
                status=GroupMember.Status.ACTIVE, role=role,
            )
        self.rotation = RotationOrder.objects.create(
            group=self.group, member=self.members[self.beneficiary.pk],
            group_settings=self.settings, contribution_period=date(2026, 11, 1),
            cycle_number=1, position=1, status=RotationOrder.Status.CURRENT,
        )
        for i, member in enumerate(self.members.values()):
            Contribution.objects.create(
                member=member, group_settings=self.settings,
                amount=Decimal("1000.00"), currency="MZN",
                contribution_period=date(2026, 11, 1),
                source=Contribution.Source.MANUAL,
                status=Contribution.Status.CONFIRMED,
                reference=f"EXTERNAL-MANUAL-{i}",
            )
        self.chain = FakeEvidenceChain()

    def prepared(self):
        d = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager
        )
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.treasurer)
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.voter2)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)
        Service.appoint_custodian(
            group_id=self.group.pk, appointed_by=self.manager,
            group_member_id=self.members[self.treasurer.pk].pk,
            provider=TreasuryMandate.Provider.MPESA, wallet_alias="M-Pesa ***1234",
        )
        return d

    def open(self, d):
        return Service.open_for_external_payment(
            disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
        )

    def report(self, d, reference="TX-EXTERNAL-0001"):
        return Service.report_external_payment(
            disbursement_id=d.pk, reported_by=self.treasurer,
            reference=reference,
        )

    def test_full_process_has_no_platform_wallet_transfer(self):
        d = self.prepared()
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.complete(disbursement_id=d.pk, completed_by=self.manager)
        self.open(d)
        self.assertEqual(self.chain.authorization_count, 1)
        self.report(d)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.AWAITING_CONFIRMATION)
        self.assertEqual(self.report(d).status, Disbursement.Status.AWAITING_CONFIRMATION)
        self.assertEqual(ExternalPaymentReport.objects.count(), 1)
        Service.respond_to_report(
            disbursement_id=d.pk, responded_by=self.beneficiary, received=True,
        )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.EVIDENCE_PENDING)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)
        completed = Service.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
        )
        self.assertEqual(completed.status, Disbursement.Status.COMPLETED)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.COMPLETED)
        self.assertEqual(self.chain.ack_count, 1)
        self.assertEqual(
            Service.finalize_acknowledged_payment(
                disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
            ).status, Disbursement.Status.COMPLETED,
        )
        self.assertEqual(self.chain.authorization_count, 1)
        self.assertEqual(self.chain.ack_count, 1)

    def test_treasurer_cannot_report_before_rn06_and_onchain_authorization(self):
        d = self.prepared()
        with self.assertRaises(InvalidDisbursementStatus):
            self.report(d)
        self.assertEqual(ExternalPaymentReport.objects.count(), 0)
        self.assertEqual(d.status, Disbursement.Status.APPROVED)

    def test_wrong_user_cannot_report_or_confirm(self):
        d = self.prepared()
        self.open(d)
        with self.assertRaises(InvalidCustodian):
            Service.report_external_payment(
                disbursement_id=d.pk, reported_by=self.manager,
                reference="TX-EXTERNAL-0001",
            )
        self.report(d)
        with self.assertRaises(UnauthorizedReceiptResponse):
            Service.respond_to_report(
                disbursement_id=d.pk, responded_by=self.treasurer, received=True,
            )

    def test_beneficiary_dispute_prevents_completion(self):
        d = self.prepared()
        self.open(d)
        self.report(d)
        Service.respond_to_report(
            disbursement_id=d.pk, responded_by=self.beneficiary,
            received=False, dispute_reason="Montante não recebido",
        )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.DISPUTED)
        with self.assertRaises(InvalidDisbursementStatus):
            Service.finalize_acknowledged_payment(
                disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
            )
        self.assertEqual(self.chain.ack_count, 0)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_no_repeated_report_with_different_reference(self):
        d = self.prepared()
        self.open(d)
        self.report(d)
        with self.assertRaises(RepeatedPaymentReport):
            self.report(d, reference="TX-EXTERNAL-0002")

    def test_chain_timeout_after_ack_is_reconciled(self):
        d = self.prepared()
        self.open(d)
        self.report(d)
        Service.respond_to_report(
            disbursement_id=d.pk, responded_by=self.beneficiary, received=True,
        )
        self.chain.fail_after_ack_once = True
        with self.assertRaises(TimeoutError):
            Service.finalize_acknowledged_payment(
                disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
            )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.EVIDENCE_PENDING)
        repaired = Service.finalize_acknowledged_payment(
            disbursement_id=d.pk, requested_by=self.manager, client=self.chain,
        )
        self.assertEqual(repaired.status, Disbursement.Status.COMPLETED)
        self.assertEqual(self.chain.ack_count, 1)


    def test_custodian_cannot_self_confirm_their_own_turn(self):
        d = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager,
        )
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.treasurer)
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.voter2)
        Service.appoint_custodian(
            group_id=self.group.pk, appointed_by=self.manager,
            group_member_id=self.members[self.beneficiary.pk].pk,
            provider=TreasuryMandate.Provider.MPESA, wallet_alias="M-Pesa ***1234",
        )
        with self.assertRaises(InvalidCustodian):
            self.open(d)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)
        self.assertEqual(self.chain.authorization_count, 0)

    def test_archived_group_blocks_late_confirmation_and_completion(self):
        d = self.prepared()
        self.open(d)
        self.report(d)
        self.group.status = Group.Status.ARCHIVED
        self.group.save(update_fields=["status"])
        with self.assertRaises(InvalidDisbursementStatus):
            Service.respond_to_report(
                disbursement_id=d.pk, responded_by=self.beneficiary, received=True,
            )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.AWAITING_CONFIRMATION)

    def test_treasury_wallet_identifier_is_bound_to_onchain_authorization(self):
        d = self.prepared()
        self.open(d)
        mandate = TreasuryMandate.objects.get(group=self.group)
        before = Service.authorization_hash(d)
        mandate.wallet_alias = "M-Pesa ***9999"
        mandate.save(update_fields=["wallet_alias"])
        # Re-read DB state instead of the cached group.treasury_mandate relation.
        fresh = Disbursement.objects.get(pk=d.pk)
        self.assertNotEqual(Service.authorization_hash(fresh), before)
        with self.assertRaises(ExternalEvidenceMismatch):
            self.open(d)


    def test_production_defaults_refuse_old_direct_completion(self):
        d = self.prepared()
        with override_settings(
            NON_CUSTODIAL_DISBURSEMENTS_ENABLED=False,
            SANDBOX_PAYMENTS_ENABLED=False,
            ALLOW_LEGACY_ADMINISTRATIVE_COMPLETION=False,
        ):
            with self.assertRaises(InvalidDisbursementStatus):
                DisbursementService.complete(
                    disbursement_id=d.pk, completed_by=self.manager,
                )
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_api_manager_only_custodian_only_and_beneficiary_only(self):
        from unittest.mock import patch
        client = APIClient()
        mandate_url = reverse("group-treasury-mandate", kwargs={"group_id": self.group.pk})
        client.force_authenticate(user=self.treasurer)
        denied = client.post(mandate_url, {
            "group_member_id": str(self.members[self.treasurer.pk].pk),
            "provider": "MPESA", "wallet_alias": "M-Pesa ***1234",
        }, format="json")
        self.assertNotEqual(denied.status_code, 201)
        d = self.prepared()
        open_url = reverse("group-disbursement-open-external", kwargs={
            "group_id": self.group.pk, "disbursement_id": d.pk,
        })
        report_url = reverse("group-disbursement-report-external", kwargs={
            "group_id": self.group.pk, "disbursement_id": d.pk,
        })
        ack_url = reverse("group-disbursement-acknowledge-external", kwargs={
            "group_id": self.group.pk, "disbursement_id": d.pk,
        })
        with patch(
            "disbursements.services.noncustodial_service.DisbursementRegistryClient",
            return_value=self.chain,
        ):
            client.force_authenticate(user=self.treasurer)
            self.assertNotEqual(client.post(open_url, {}, format="json").status_code, 200)
            client.force_authenticate(user=self.manager)
            self.assertEqual(client.post(open_url, {}, format="json").status_code, 200)
        client.force_authenticate(user=self.manager)
        self.assertNotEqual(
            client.post(report_url, {"transfer_reference": "TX-EXTERNAL-0001"}, format="json").status_code,
            200,
        )
        client.force_authenticate(user=self.treasurer)
        self.assertEqual(
            client.post(report_url, {"transfer_reference": "TX-EXTERNAL-0001"}, format="json").status_code,
            200,
        )
        self.assertNotEqual(
            client.post(ack_url, {"received": True}, format="json").status_code,
            200,
        )
        client.force_authenticate(user=self.beneficiary)
        self.assertEqual(
            client.post(ack_url, {"received": True}, format="json").status_code,
            200,
        )
