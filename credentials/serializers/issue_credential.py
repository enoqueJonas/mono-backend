from rest_framework import serializers


class IssueContributionCredentialSerializer(serializers.Serializer):
    group_member_id = serializers.UUIDField()

    period_start = serializers.DateField()

    period_end = serializers.DateField()

    def validate(self, attrs):
        if attrs["period_end"] < attrs["period_start"]:
            raise serializers.ValidationError(
                {
                    "period_end": (
                        "The end period must be equal to or later "
                        "than the start period."
                    )
                }
            )

        return attrs
