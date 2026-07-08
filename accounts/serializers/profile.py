from rest_framework import serializers

from accounts.models import User


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "is_active",
            "created_at",
        )
