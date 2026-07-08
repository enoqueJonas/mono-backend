from rest_framework import serializers

from accounts.utils.phone import normalize_mz_phone


class LoginSerializer(serializers.Serializer):

    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_phone_number(self, value):

        return normalize_mz_phone(value)
