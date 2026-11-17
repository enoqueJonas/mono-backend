from django.conf import settings
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
    payout_required = serializers.SerializerMethodField()
    payout_status = serializers.SerializerMethodField()
    payout_reference = serializers.SerializerMethodField()
    payout_transaction_id = serializers.SerializerMethodField()

    def get_payout_required(self, obj):
        return bool(getattr(settings, "DISBURSEMENT_PAYOUT_REQUIRED", False))

    def get_payout_status(self, obj):
        return obj.execution.status if hasattr(obj, "execution") else None

    def get_payout_reference(self, obj):
        return obj.execution.reference if hasattr(obj, "execution") else None

    def get_payout_transaction_id(self, obj):
        return obj.execution.provider_transaction_id if hasattr(obj, "execution") else None

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
            "payout_required",
            "payout_status",
            "payout_reference",
            "payout_transaction_id",
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
