from rest_framework import serializers

from groups.models import GroupSettings


class CreateGroupSettingsSerializer(serializers.Serializer):
    contribution_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    contribution_frequency = serializers.ChoiceField(
        choices=GroupSettings.ContributionFrequency.choices,
    )
    maximum_members = serializers.IntegerField(min_value=2)
    rotation_strategy = serializers.ChoiceField(
        choices=GroupSettings.RotationStrategy.choices,
    )
    requires_consensus = serializers.BooleanField(default=True)
    allow_manual_contributions = serializers.BooleanField(default=False)


class CreateGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    settings = CreateGroupSettingsSerializer()
