from rest_framework import serializers

from groups.models import GroupSettings


class UpdateGroupSettingsSerializer(serializers.Serializer):
    contribution_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        required=False,
    )

    contribution_frequency = serializers.ChoiceField(
        choices=GroupSettings.ContributionFrequency.choices,
        required=False,
    )

    maximum_members = serializers.IntegerField(
        min_value=2,
        required=False,
    )

    rotation_strategy = serializers.ChoiceField(
        choices=GroupSettings.RotationStrategy.choices,
        required=False,
    )

    requires_consensus = serializers.BooleanField(
        required=False,
    )

    allow_manual_contributions = serializers.BooleanField(
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "At least one setting must be provided."
            )

        return attrs
