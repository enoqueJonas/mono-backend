from rest_framework import serializers


class DesignateCustodianSerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    provider = serializers.ChoiceField(choices=("M_PESA", "E_MOLA"))
    wallet_number = serializers.RegexField(regex=r"^\+?[0-9]{9,15}$", max_length=32)


class ReportExternalPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField(min_length=4, max_length=120, trim_whitespace=True)
    recipient_wallet_number = serializers.RegexField(
        regex=r"^\+?[0-9]{9,15}$", max_length=32
    )


class DisputeExternalPaymentSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=8, max_length=1000, trim_whitespace=True)
