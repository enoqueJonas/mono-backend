from core.exceptions import DomainException
from groups.models import GroupMember


class NotGroupMember(DomainException):
    default_message = "You are not an active member of this group."


class GroupMemberService:

    @staticmethod
    def ensure_active_member(*, group_id, user):
        member = GroupMember.objects.filter(
            group_id=group_id,
            user=user,
            status=GroupMember.Status.ACTIVE,
        ).first()

        if member is None:
            raise NotGroupMember()

        return member
