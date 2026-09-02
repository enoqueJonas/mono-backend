from rest_framework import serializers


class MobileWalletContributionSerializer(

    serializers.Serializer

):

    group_id = serializers.UUIDField()

    group_member_id = serializers.UUIDField()

    amount = serializers.DecimalField(

        max_digits=12,

        decimal_places=2,

    )

    currency = serializers.CharField(

        max_length=3,

    )

    contribution_period = serializers.DateField()

    reference = serializers.CharField(

        max_length=100,

    )
