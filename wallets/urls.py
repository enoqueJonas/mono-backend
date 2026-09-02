from django.urls import path

from wallets.views import (
    MobileWalletContributionWebhookView,
)


urlpatterns = [
    path(
        "contributions/confirmation/",
        MobileWalletContributionWebhookView.as_view(),
        name="mobile-wallet-contribution-webhook",
    ),
]
