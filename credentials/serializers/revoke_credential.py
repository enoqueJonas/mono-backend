from rest_framework import serializers


class RevokeCredentialSerializer(
    serializers.Serializer,
):
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
