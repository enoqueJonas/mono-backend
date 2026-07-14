from rest_framework import serializers

from credentials.models import VerifiableCredential


class VerifiableCredentialSerializer(
    serializers.ModelSerializer
):
    effective_status = serializers.CharField(
        read_only=True,
    )

    group_id = serializers.UUIDField(
        source="group_member.group_id",
        read_only=True,
    )

    group_name = serializers.CharField(
        source="group_member.group.name",
        read_only=True,
    )

    group_member_id = serializers.UUIDField(
        source="group_member.id",
        read_only=True,
    )

    holder_user_id = serializers.UUIDField(
        source="group_member.user_id",
        read_only=True,
    )

    holder_name = serializers.SerializerMethodField()

    issuer = serializers.CharField(
        source="issuer_did.did",
        read_only=True,
    )

    holder = serializers.CharField(
        source="holder_did.did",
        read_only=True,
    )

    issued_by_name = serializers.SerializerMethodField()

    class Meta:
        model = VerifiableCredential
        fields = (
            "id",
            "credential_type",
            "effective_status",
            "group_id",
            "group_name",
            "group_member_id",
            "holder_user_id",
            "holder_name",
            "issuer",
            "holder",
            "issued_by_name",
            "period_start",
            "period_end",
            "valid_from",
            "valid_until",
            "credential_hash",
            "credential_document",
            "revoked_at",
            "revocation_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_holder_name(self, obj):
        user = obj.group_member.user

        return (
            f"{user.first_name} {user.last_name}"
        ).strip()

    def get_issued_by_name(self, obj):
        user = obj.issued_by.user

        return (
            f"{user.first_name} {user.last_name}"
        ).strip()
