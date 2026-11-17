from rest_framework import serializers

from disbursements.models import ExternalPaymentReport, TreasuryMandate


class AppointTreasuryMandateSerializer(serializers.Serializer):
    group_member_id = serializers.UUIDField()
    provider = serializers.ChoiceField(choices=TreasuryMandate.Provider.choices)
    wallet_alias = serializers.CharField(max_length=64, min_length=4)


class TreasuryMandateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreasuryMandate
        fields = (
            "id", "group", "custodian", "provider", "wallet_alias",
            "appointed_by", "appointed_at",
        )
        read_only_fields = fields


class ExternalPaymentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPaymentReport
        fields = (
            "id", "disbursement", "provider", "wallet_alias",
            "transfer_reference", "amount", "currency",
            "reported_by", "beneficiary_user", "reported_at",
            "status", "confirmed_by", "responded_at", "dispute_reason",
        )
        read_only_fields = fields


class ReportExternalPaymentSerializer(serializers.Serializer):
    transfer_reference = serializers.RegexField(
        regex=r"^[A-Za-z0-9][A-Za-z0-9._/-]{4,99}$",
        max_length=100,
        help_text="Transaction reference reported by the external custodian.",
    )


class AcknowledgeExternalPaymentSerializer(serializers.Serializer):
    received = serializers.BooleanField()
    dispute_reason = serializers.CharField(
        required=False, allow_blank=True, max_length=1200,
    )

    def validate(self, attrs):
        if not attrs["received"] and not attrs.get("dispute_reason", "").strip():
            raise serializers.ValidationError(
                {"dispute_reason": "Explique por que razão contesta o recebimento."}
            )
        return attrs
