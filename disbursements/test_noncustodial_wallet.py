"""No-custody flow: an approved withdrawal is an external human transfer."""
from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from contributions.models import Contribution
from disbursements.models import (
    Disbursement, ExternalPaymentReport, ExternalWalletCustody,
)
from disbursements.services.disbursement_service import (
    DisbursementService, InvalidDisbursementStatus,
)
from disbursements.services.external_wallet_service import (
    ExternalWalletService, MissingCustodian, WrongCustodian,
    PaymentEvidenceConflict, ReceiptActorNotEligible,
)
from groups.models import Group, GroupMember, GroupSettings, RotationOrder


@override_settings(NONCUSTODIAL_WALLET_FLOW_ENABLED=True)
class NoncustodialWalletFlowTests(TestCase):
    def setUp(self):
        self.users = [
            User.objects.create_user(
                phone_number=f"+25884999110{i}", password="test-only-password"
            ) for i in range(6)
        ]
        self.manager, self.treasurer, self.beneficiary, self.voter1, self.voter2, self.outsider = self.users
        self.group = Group.objects.create(name="Grupo sem custódia na plataforma")
        self.settings = GroupSettings.objects.create(
            group=self.group, version=1, is_active=True,
            contribution_amount=Decimal("1000.00"), currency="MZN",
            contribution_frequency=GroupSettings.ContributionFrequency.MONTHLY,
            maximum_members=7, rotation_strategy=GroupSettings.RotationStrategy.FIXED_ORDER,
            requires_consensus=True, allow_manual_contributions=True,
        )
        self.members = {}
        for u, role in [
            (self.manager, GroupMember.Role.MANAGER),
            (self.treasurer, GroupMember.Role.TREASURER),
            (self.beneficiary, GroupMember.Role.MEMBER),
            (self.voter1, GroupMember.Role.MEMBER),
            (self.voter2, GroupMember.Role.MEMBER),
        ]:
            self.members[u.pk] = GroupMember.objects.create(
                group=self.group, user=u, role=role,
                status=GroupMember.Status.ACTIVE,
            )
        self.rotation = RotationOrder.objects.create(
            group=self.group, member=self.members[self.beneficiary.pk],
            group_settings=self.settings, cycle_number=1, position=1,
            contribution_period=date(2026, 11, 1),
            status=RotationOrder.Status.CURRENT,
        )
        for i, member in enumerate(self.members.values()):
            Contribution.objects.create(
                member=member, group_settings=self.settings,
                amount=Decimal("1000.00"), currency="MZN",
                status=Contribution.Status.CONFIRMED,
                source=Contribution.Source.MANUAL,
                contribution_period=date(2026, 11, 1),
                reference=f"NONCUSTODIAL-CONTRIB-{i}",
            )
        self.reference = "MPESA-TEST-20261117-001"
        self.beneficiary_wallet = "+258849991102"

    def designate(self, user=None):
        return ExternalWalletService.designate_custodian(
            group_id=self.group.pk,
            designated_by=self.manager,
            member_id=self.members[(user or self.treasurer).pk].pk,
            provider="M_PESA",
            wallet_number="+258849991101",
        )

    def approve(self):
        d = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager
        )
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.voter1)
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.voter2)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)
        return d

    def report(self, d, **kwargs):
        return ExternalWalletService.report_payment(
            disbursement_id=d.pk,
            reported_by=kwargs.get("reported_by", self.treasurer),
            reference=kwargs.get("reference", self.reference),
            recipient_wallet_number=kwargs.get("number", self.beneficiary_wallet),
        )

    def test_custodian_required_before_rn06_proposal(self):
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.create(
                group_id=self.group.pk, cycle_number=1, created_by=self.manager
            )
        self.assertFalse(Disbursement.objects.exists())

    def test_treasurer_designation_and_custody_frozen_at_proposal(self):
        self.designate()
        d = self.approve()
        self.assertEqual(d.custodian_at_proposal_id, self.members[self.treasurer.pk].pk)
        self.assertEqual(d.custody_provider_at_proposal, "M_PESA")
        self.assertEqual(d.custody_wallet_at_proposal, "+258849991101")
        with self.assertRaises(PaymentEvidenceConflict):
            ExternalWalletService.designate_custodian(
                group_id=self.group.pk,
                designated_by=self.manager,
                member_id=self.members[self.manager.pk].pk,
                provider="E_MOLA",
                wallet_number="+258849991100",
            )

    def test_rn06_and_manual_receipt_workflow(self):
        self.designate()
        d = self.approve()
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.complete(disbursement_id=d.pk, completed_by=self.manager)
        r = self.report(d)
        self.assertEqual(r.status, ExternalPaymentReport.Status.REPORTED)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.PAYMENT_REPORTED)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

        with self.assertRaises(ReceiptActorNotEligible):
            ExternalWalletService.confirm_receipt(
                disbursement_id=d.pk, confirmed_by=self.treasurer
            )
        result = ExternalWalletService.confirm_receipt(
            disbursement_id=d.pk, confirmed_by=self.beneficiary
        )
        self.assertEqual(result.status, Disbursement.Status.COMPLETED)
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.COMPLETED)
        r.refresh_from_db()
        self.assertEqual(r.status, ExternalPaymentReport.Status.CONFIRMED)
        self.assertEqual(r.confirmed_by, self.beneficiary)
        self.assertIsNotNone(r.confirmed_at)
        self.assertEqual(
            ExternalWalletService.confirm_receipt(
                disbursement_id=d.pk, confirmed_by=self.beneficiary
            ).status, Disbursement.Status.COMPLETED
        )

    def test_only_designated_custodian_can_report(self):
        self.designate()
        d = self.approve()
        with self.assertRaises(WrongCustodian):
            self.report(d, reported_by=self.manager)
        with self.assertRaises(WrongCustodian):
            self.report(d, reported_by=self.outsider)
        self.assertFalse(ExternalPaymentReport.objects.exists())
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.APPROVED)

    def test_idempotent_report_cannot_change_reference_or_recipient(self):
        self.designate()
        d = self.approve()
        first = self.report(d)
        self.assertEqual(first.pk, self.report(d).pk)
        self.assertEqual(ExternalPaymentReport.objects.count(), 1)
        with self.assertRaises(PaymentEvidenceConflict):
            self.report(d, reference="MPESA-TEST-20261117-002")
        with self.assertRaises(PaymentEvidenceConflict):
            self.report(d, number="+258849991199")

    def test_dispute_blocks_rotation_and_confirmation(self):
        self.designate()
        d = self.approve()
        self.report(d)
        r = ExternalWalletService.dispute_receipt(
            disbursement_id=d.pk,
            disputed_by=self.beneficiary,
            reason="A referência não corresponde a qualquer valor recebido.",
        )
        self.assertEqual(r.status, ExternalPaymentReport.Status.DISPUTED)
        d.refresh_from_db()
        self.assertEqual(d.status, Disbursement.Status.DISPUTED)
        with self.assertRaises(InvalidDisbursementStatus):
            ExternalWalletService.confirm_receipt(
                disbursement_id=d.pk, confirmed_by=self.beneficiary
            )
        self.rotation.refresh_from_db()
        self.assertEqual(self.rotation.status, RotationOrder.Status.CURRENT)

    def test_member_not_manager_or_treasurer_cannot_hold_custody(self):
        with self.assertRaises(WrongCustodian):
            self.designate(self.voter1)

    def test_custodian_cannot_be_beneficiary_in_same_cycle(self):
        # Beneficiary is temporarily designated as treasurer.
        beneficiary_m = self.members[self.beneficiary.pk]
        beneficiary_m.role = GroupMember.Role.TREASURER
        beneficiary_m.save(update_fields=["role", "updated_at"])
        self.designate(self.beneficiary)
        with self.assertRaises(InvalidDisbursementStatus):
            DisbursementService.create(
                group_id=self.group.pk, cycle_number=1, created_by=self.manager
            )

    def test_api_prevents_manager_report_and_allows_beneficiary_confirmation(self):
        self.designate()
        d = self.approve()
        report_url = reverse("group-external-payment-report", kwargs={
            "group_id": self.group.pk, "disbursement_id": d.pk,
        })
        confirm_url = reverse("group-external-payment-confirm", kwargs={
            "group_id": self.group.pk, "disbursement_id": d.pk,
        })
        client = APIClient()
        payload = {
            "reference": self.reference,
            "recipient_wallet_number": self.beneficiary_wallet,
        }
        client.force_authenticate(user=self.manager)
        bad = client.post(report_url, payload, format="json")
        self.assertNotEqual(bad.status_code, 200)
        self.assertFalse(ExternalPaymentReport.objects.exists())
        client.force_authenticate(user=self.treasurer)
        response = client.post(report_url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["verification_level"], "UNVERIFIED_CLAIM")
        client.force_authenticate(user=self.beneficiary)
        response = client.post(confirm_url, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["external_payment"]["verification_level"], "BENEFICIARY_ATTESTED")

    def test_proposal_cannot_be_approved_by_manager_only(self):
        self.designate()
        d = DisbursementService.create(
            group_id=self.group.pk, cycle_number=1, created_by=self.manager
        )
        DisbursementService.approve(disbursement_id=d.pk, approved_by=self.voter1)
        with self.assertRaises(InvalidDisbursementStatus):
            self.report(d)
        self.assertFalse(ExternalPaymentReport.objects.exists())

    @override_settings(NONCUSTODIAL_WALLET_FLOW_ENABLED=False)
    def test_disabled_by_default_cannot_report(self):
        from disbursements.services.external_wallet_service import ExternalWalletFlowUnavailable
        with self.assertRaises(ExternalWalletFlowUnavailable):
            ExternalWalletService.report_payment(
                disbursement_id="00000000-0000-0000-0000-000000000000",
                reported_by=self.treasurer,
                reference=self.reference,
                recipient_wallet_number=self.beneficiary_wallet,
            )
