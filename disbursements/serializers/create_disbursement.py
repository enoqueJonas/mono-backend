from rest_framework import serializers


class CreateDisbursementSerializer(serializers.Serializer):
    cycle_number = serializers.IntegerField(
        min_value=1,
    )
