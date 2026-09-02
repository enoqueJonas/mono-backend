from rest_framework import serializers

from groups.models import RotationOrder


class RotationOrderSerializer(

    serializers.ModelSerializer

):

    member_name = serializers.SerializerMethodField()

    member_phone_number = serializers.CharField(

        source="member.user.phone_number",

        read_only=True,

    )

    settings_version = serializers.IntegerField(

        source="group_settings.version",

        read_only=True,

    )

    class Meta:

        model = RotationOrder

        fields = (

            "id",

            "member",

            "member_name",

            "member_phone_number",

            "cycle_number",

            "position",

            "status",

            "contribution_period",

            "group_settings",

            "settings_version",

        )

        read_only_fields = fields

    def get_member_name(self, obj):

        user = obj.member.user

        full_name = (

            f"{user.first_name} {user.last_name}"

        ).strip()

        return full_name or user.phone_number


class GenerateRotationSerializer(

    serializers.Serializer

):

    cycle_number = serializers.IntegerField(

        min_value=1,

    )

    contribution_period = serializers.DateField()
