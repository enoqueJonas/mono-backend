from rest_framework import serializers

from identity.models import UserDID


class UserDIDSerializer(serializers.ModelSerializer):
    verification_method_id = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = UserDID
        fields = (
            "id",
            "did",
            "method",
            "status",
            "public_key_multibase",
            "verification_method_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
