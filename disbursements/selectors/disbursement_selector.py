from disbursements.models import Disbursement


class DisbursementSelector:

    @staticmethod
    def list_group_disbursements(*, group_id):
        return (
            Disbursement.objects
            .select_related(
                "group",
                "beneficiary",
                "beneficiary__user",
                "rotation_order",
                "group_settings",
            )
            .filter(group_id=group_id)
            .order_by("-created_at")
        )

    @staticmethod
    def get_group_disbursement(
        *,
        group_id,
        disbursement_id,
    ):
        return (
            Disbursement.objects
            .select_related(
                "group",
                "beneficiary",
                "beneficiary__user",
                "rotation_order",
                "group_settings",
            )
            .filter(
                id=disbursement_id,
                group_id=group_id,
            )
            .first()
        )
