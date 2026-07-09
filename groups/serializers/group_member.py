from rest_framework import serializers

from groups.models import GroupMember


class GroupMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user.id", read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.CharField(
        source="user.phone_number", read_only=True)

    class Meta:
        model = GroupMember
        fields = (
            "id",
            "user_id",
            "full_name",
            "phone_number",
            "role",
            "status",
            "joined_at",
        )

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
