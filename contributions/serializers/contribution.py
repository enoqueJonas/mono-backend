from rest_framework import serializers

from contributions.models import Contribution


class ContributionSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    group_name = serializers.SerializerMethodField()

    class Meta:
        model = Contribution
        fields = (
            "id",
            "member",
            "member_name",
            "group_name",
            "amount",
            "contribution_period",
            "reference",
            "source",
            "status",
            "created_at",
        )

    def get_member_name(self, obj):
        return f"{obj.member.user.first_name} {obj.member.user.last_name}"

    def get_group_name(self, obj):
        return obj.member.group.name
