from credentials.models import VerifiableCredential
from groups.models import GroupMember


class CredentialSelector:
    @staticmethod
    def _base_queryset():
        return (
            VerifiableCredential.objects
            .select_related(
                "group_member",
                "group_member__user",
                "group_member__group",
                "issued_by",
                "issued_by__user",
                "issuer_did",
                "holder_did",
            )
        )

    @classmethod
    def list_for_holder(cls, *, user):
        return (
            cls._base_queryset()
            .filter(
                group_member__user=user,
            )
            .order_by("-valid_from")
        )

    @classmethod
    def get_accessible_credential(
        cls,
        *,
        credential_id,
        user,
    ):
        credential = (
            cls._base_queryset()
            .filter(id=credential_id)
            .first()
        )

        if credential is None:
            return None

        if credential.group_member.user_id == user.id:
            return credential

        is_group_manager = GroupMember.objects.filter(
            group_id=credential.group_member.group_id,
            user=user,
            role=GroupMember.Role.MANAGER,
            status=GroupMember.Status.ACTIVE,
        ).exists()

        if is_group_manager:
            return credential

        return None
