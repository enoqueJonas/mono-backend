from django.urls import path

from disbursements.views import (

    GroupDisbursementApproveView,

    GroupDisbursementCompleteView,
    GroupExternalWalletCustodyView,
    GroupExternalPaymentReportView,
    GroupExternalPaymentConfirmView,
    GroupExternalPaymentDisputeView,

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
]

urlpatterns += [
    path(
        "groups/<uuid:group_id>/external-wallet-custody/",
        GroupExternalWalletCustodyView.as_view(),
        name="group-external-wallet-custody",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/report-payment/",
        GroupExternalPaymentReportView.as_view(),
        name="group-external-payment-report",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/confirm-receipt/",
        GroupExternalPaymentConfirmView.as_view(),
        name="group-external-payment-confirm",
    ),
    path(
        "groups/<uuid:group_id>/disbursements/<uuid:disbursement_id>/dispute-receipt/",
        GroupExternalPaymentDisputeView.as_view(),
        name="group-external-payment-dispute",
    ),
]
