from rest_framework import serializers

from groups.models import Group, GroupSettings


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
    settings = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "description",
            "status",
            "settings",
            "user_role",
            "created_at",
            "updated_at",
        )

    def get_settings(self, obj):
        settings = obj.settings_versions.filter(is_active=True).first()

        if settings is None:
            return None

        return GroupSettingsSerializer(settings).data

    def get_user_role(self, obj):
        user = self.context.get("user")

        if user is None:
            return None

        membership = obj.members.filter(user=user).first()

        if membership is None:
            return None

        return membership.role


class GroupDetailSerializer(GroupSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ("statistics",)

    def get_statistics(self, obj):
        statistics = self.context.get("statistics")

        return GroupStatisticsSerializer(statistics).data
