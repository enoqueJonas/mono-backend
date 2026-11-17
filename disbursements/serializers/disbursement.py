from rest_framework import serializers

from disbursements.models import Disbursement


class DisbursementSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(
        source="group.name",
        read_only=True,
    )

    beneficiary_name = serializers.SerializerMethodField()

    rotation_position = serializers.IntegerField(
        source="rotation_order.position",
        read_only=True,
    )

    contribution_period = serializers.DateField(
        source="rotation_order.contribution_period",
        read_only=True,
    )

    settings_version = serializers.IntegerField(
        source="group_settings.version",
        read_only=True,
    )

    approval_count = serializers.SerializerMethodField()
    approved_by_ids = serializers.SerializerMethodField()

    external_payment = serializers.SerializerMethodField()

    def get_external_payment(self, obj):
        from disbursements.models import ExternalPaymentReport
        report = ExternalPaymentReport.objects.filter(disbursement=obj).first()
        if report is None:
            return None
        return {
            "provider": report.provider,
            "reference": report.reference,
            "recipient_wallet_number": report.recipient_wallet_number,
            "reported_by": str(report.reported_by_id),
            "status": report.status,
            "reported_at": report.reported_at,
            "confirmed_by": str(report.confirmed_by_id) if report.confirmed_by_id else None,
            "confirmed_at": report.confirmed_at,
            "disputed_at": report.disputed_at,
            "dispute_reason": report.dispute_reason,
            "verification_level": "BENEFICIARY_ATTESTED" if report.confirmed_at else "UNVERIFIED_CLAIM",
        }


    def get_approval_count(self, obj):
        return obj.approvals.count()

    def get_approved_by_ids(self, obj):
        return [str(value) for value in obj.approvals.values_list("approved_by_id", flat=True)]

    class Meta:
        model = Disbursement
        fields = (
            "id",
            "group",
            "group_name",
            "beneficiary",
            "beneficiary_name",
            "rotation_order",
            "rotation_position",
            "group_settings",
            "settings_version",
            "cycle_number",
            "contribution_period",
            "amount",
            "currency",
            "status",
            "requested_at",
            "proposed_by",
            "required_approvals",
            "approval_count",
            "approved_by_ids",
            "eligible_approver_ids",
            "custodian_at_proposal",
            "custody_provider_at_proposal",
            "custody_wallet_at_proposal",
            "external_payment",
            "completed_at",
            "failure_reason",
            "created_at",
            "updated_at",
        )

        read_only_fields = fields

    def get_beneficiary_name(self, obj):
        user = obj.beneficiary.user

        full_name = (
            f"{user.first_name} {user.last_name}"
        ).strip()

        return full_name or user.phone_number
