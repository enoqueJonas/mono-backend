from rest_framework import serializers

from accounts.models.user import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "role",
        )
