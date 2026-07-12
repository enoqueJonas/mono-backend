from rest_framework import serializers

from groups.models import Group, GroupSettings


class GroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSettings
        fields = (
            "contribution_amount",
            "contribution_frequency",
            "maximum_members",
            "rotation_strategy",
            "requires_consensus",
            "allow_manual_contributions",
        )


class GroupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSettings
        fields = (
            "contribution_amount",
            "currency",
            "contribution_frequency",
            "maximum_members",
            "rotation_strategy",
            "requires_consensus",
            "allow_manual_contributions",
        )


class GroupStatisticsSerializer(serializers.Serializer):
    active_members = serializers.IntegerField()
    maximum_members = serializers.IntegerField()
    confirmed_contributions = serializers.IntegerField()
    pending_contributions = serializers.IntegerField()
    total_confirmed_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )


class GroupSerializer(serializers.ModelSerializer):
    settings = GroupSettingsSerializer(read_only=True)

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "description",
            "status",
            "settings",
            "created_at",
            "updated_at",
        )


class GroupDetailSerializer(GroupSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ("statistics",)

    def get_statistics(self, obj):
        statistics = self.context.get("statistics")

        return GroupStatisticsSerializer(statistics).data
