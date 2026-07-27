from dataclasses import dataclass

from groups.models import GroupMember
from identity.models import (
    GroupDID,
    UserDID,
)


@dataclass(frozen=True, slots=True)
class CredentialIssuanceContext:
    group_member: GroupMember
    user_did: UserDID
    group_did: GroupDID
