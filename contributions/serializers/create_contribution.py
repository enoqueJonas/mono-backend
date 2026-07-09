from rest_framework import serializers


class CreateContributionSerializer(serializers.Serializer):
    group_member_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    contribution_period = serializers.DateField()
