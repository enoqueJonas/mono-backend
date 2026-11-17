from django.test import SimpleTestCase, override_settings

from wallets.mpesa_b2c import MpesaConfigurationError, MpesaGateway


class MpesaB2CGateTests(SimpleTestCase):
    @override_settings(MPESA_B2C_ENABLED=False)
    def test_disabled_configuration_cannot_send_money(self):
        with self.assertRaisesRegex(MpesaConfigurationError, "disabled"):
            MpesaGateway()

    @override_settings(
        MPESA_B2C_ENABLED=True,
        MPESA_B2C_HOST="https://api.vm.co.mz",
        MPESA_B2C_API_KEY="not-a-real-key",
        MPESA_B2C_PUBLIC_KEY="not-a-real-key",
        MPESA_B2C_SERVICE_PROVIDER_CODE="000000",
    )
    def test_live_b2c_is_blocked_without_verified_funds_ledger(self):
        with self.assertRaisesRegex(MpesaConfigurationError, "Production B2C blocked"):
            MpesaGateway()

    @override_settings(
        MPESA_B2C_ENABLED=True,
        MPESA_B2C_HOST="http://api.sandbox.vm.co.mz",
    )
    def test_insecure_http_endpoint_is_refused(self):
        with self.assertRaisesRegex(MpesaConfigurationError, "approved HTTPS"):
            MpesaGateway()
