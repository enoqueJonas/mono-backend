from rest_framework import serializers


class VerifyCredentialSerializer(serializers.Serializer):
    credential = serializers.JSONField()
