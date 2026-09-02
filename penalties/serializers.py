from rest_framework import serializers

from penalties.models import Penalty


class CreatePenaltySerializer(serializers.Serializer):
    member_id = serializers.UUIDField()
    reason = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


class PenaltySerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = Penalty
        fields = (
            "id",
            "member",
            "member_name",
            "reason",
            "status",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_member_name(self, obj):
        user = obj.member.user

        full_name = (
            f"{user.first_name} {user.last_name}"
        ).strip()

        return full_name or user.phone_number
