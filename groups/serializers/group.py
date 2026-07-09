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
        )
