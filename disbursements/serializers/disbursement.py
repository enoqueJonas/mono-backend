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
