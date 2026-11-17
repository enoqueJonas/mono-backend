from django.urls import path

from disbursements.views import (

    GroupDisbursementApproveView,

    GroupDisbursementCompleteView,
    GroupSandboxDisbursementExecuteView,

    GroupDisbursementDetailView,

    GroupDisbursementListCreateView,
    GroupTreasuryMandateView,
    ExternalDisbursementOpenView,
    ExternalDisbursementReportView,
    ExternalDisbursementAcknowledgeView,
    ExternalDisbursementFinalizeView,

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
]

urlpatterns += [
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/sandbox-execute/",
        GroupSandboxDisbursementExecuteView.as_view(),
        name="group-disbursement-sandbox-execute",
    ),
]

urlpatterns += [
    path(
        "groups/<uuid:group_id>/treasury-mandate/",
        GroupTreasuryMandateView.as_view(),
        name="group-treasury-mandate",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/open-external/",
        ExternalDisbursementOpenView.as_view(),
        name="group-disbursement-open-external",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/report-external/",
        ExternalDisbursementReportView.as_view(),
        name="group-disbursement-report-external",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/acknowledge-external/",
        ExternalDisbursementAcknowledgeView.as_view(),
        name="group-disbursement-acknowledge-external",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/finalize-external/",
        ExternalDisbursementFinalizeView.as_view(),
        name="group-disbursement-finalize-external",
    ),
]
