from django.urls import path
from disbursements.payout_views import (
    GroupDisbursementExecuteView,
    GroupDisbursementReconcileView,
    GroupDisbursementRecoverProofView,
)

from disbursements.views import (

    GroupDisbursementApproveView,

    GroupDisbursementCompleteView,

    GroupDisbursementDetailView,

    GroupDisbursementListCreateView,

)

urlpatterns = [
    path(
        "groups/<uuid:group_id>/disbursements/",
        GroupDisbursementListCreateView.as_view(),
        name="group-disbursement-list-create",
    ),
    path(
        (
            "groups/<uuid:group_id>/disbursements/"
            "<uuid:disbursement_id>/"
        ),
        GroupDisbursementDetailView.as_view(),
        name="group-disbursement-detail",
    ),
    path(
        (
            "groups/<uuid:group_id>/disbursements/"
            "<uuid:disbursement_id>/approve/"
        ),
        GroupDisbursementApproveView.as_view(),
        name="group-disbursement-approve",
    ),
    path(
        (
            "groups/<uuid:group_id>/disbursements/"
            "<uuid:disbursement_id>/complete/"
        ),
        GroupDisbursementCompleteView.as_view(),
        name="group-disbursement-complete",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/execute/",
        GroupDisbursementExecuteView.as_view(),
        name="group-disbursement-execute",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/reconcile/",
        GroupDisbursementReconcileView.as_view(),
        name="group-disbursement-reconcile",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/recover-proof/",
        GroupDisbursementRecoverProofView.as_view(),
        name="group-disbursement-recover-proof",
    ),
]
