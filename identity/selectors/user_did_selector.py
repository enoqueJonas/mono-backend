from identity.models import UserDID


class UserDIDSelector:
    @staticmethod
    def get_for_user(*, user) -> UserDID | None:
        return (
            UserDID.objects
            .select_related("user")
            .filter(user=user)
            .first()
        )
