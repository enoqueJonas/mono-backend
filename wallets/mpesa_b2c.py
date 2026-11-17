"""M-Pesa Mozambique B2C adapter, disabled unless provisioned by the operator.

This is NOT an offline success simulator. A request acknowledgement never
means that the beneficiary has been paid. We reconcile via provider status.
"""
import base64
from decimal import Decimal
from urllib.parse import urlsplit

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.conf import settings


class MpesaConfigurationError(RuntimeError):
    pass


class MpesaGateway:
    ALLOWED_HOSTS = {"api.vm.co.mz", "api.sandbox.vm.co.mz"}

    def __init__(self):
        if not getattr(settings, "MPESA_B2C_ENABLED", False):
            raise MpesaConfigurationError("M-Pesa B2C disabled; no financial transfer is permitted.")
        self.url = getattr(settings, "MPESA_B2C_HOST", "")
        parsed = urlsplit(self.url)
        if parsed.scheme != "https" or parsed.hostname not in self.ALLOWED_HOSTS or parsed.port not in (None, 443):
            raise MpesaConfigurationError("M-Pesa host must be an approved HTTPS host.")
        # The prototype has no independently verified C2B custody ledger.
        # A production B2C transfer could spend pooled funds based on fake
        # manually confirmed contributions. Fail closed until that boundary
        # is built, audited and permitted by the licensed operator.
        if parsed.hostname != "api.sandbox.vm.co.mz":
            raise MpesaConfigurationError(
                "Production B2C blocked: independent incoming-funds verification "
                "and regulated group custody are not implemented."
            )
        self.api_key = getattr(settings, "MPESA_B2C_API_KEY", "")
        self.public_key = getattr(settings, "MPESA_B2C_PUBLIC_KEY", "")
        self.service_code = getattr(settings, "MPESA_B2C_SERVICE_PROVIDER_CODE", "")
        if not all((self.api_key, self.public_key, self.service_code)):
            raise MpesaConfigurationError("M-Pesa B2C credentials are incomplete.")
        try:
            key = serialization.load_der_public_key(base64.b64decode(self.public_key))
            secret = key.encrypt(self.api_key.encode("utf-8"), padding.PKCS1v15())
            self.authorization = base64.b64encode(secret).decode("ascii")
        except Exception as exc:
            raise MpesaConfigurationError("Invalid B2C public-key configuration.") from exc

    def _call(self, suffix, payload):
        response = requests.post(
            self.url.rstrip("/") + suffix,
            headers={
                "Authorization": "Bearer " + self.authorization,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=(5, 30),
            allow_redirects=False,
        )
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise ValueError("Unexpected B2C response format.")
        return body

    def send(self, execution):
        response = self._call("/ipg/v1x/b2cPayment/", {
            "input_Amount": str(execution.amount),
            "input_CustomerMSISDN": execution.recipient_msisdn,
            "input_ServiceProviderCode": self.service_code,
            "input_ThirdPartyReference": execution.reference,
            "input_TransactionReference": execution.reference[:30],
        })
        if response.get("output_ResponseCode") != "INS-0":
            raise ValueError("M-Pesa rejected the B2C request.")
        # Acknowledgement only: never set FINANCIALLY_CONFIRMED here.
        return {"status": "PENDING", "transaction_id": str(response.get("output_TransactionID") or "")}

    def query(self, execution):
        response = self._call("/ipg/v1x/queryTransactionStatus/", {
            "input_ThirdPartyReference": execution.reference,
            "input_QueryReference": execution.provider_transaction_id or execution.reference,
            "input_ServiceProviderCode": self.service_code,
        })
        state = response.get("output_TransactionStatus") or response.get("output_TransactionState")
        reference = response.get("output_ThirdPartyReference")
        amount = response.get("output_Amount")
        recipient = response.get("output_CustomerMSISDN")
        transaction_id = str(response.get("output_TransactionID") or execution.provider_transaction_id)
        # Fail closed: absence of an authenticated *matching* financial record
        # is NOT confirmation. Provider field mapping requires contract tests.
        if reference != execution.reference or not transaction_id:
            return {"status": "UNKNOWN"}
        if state in ("F", "FAILED", "FAILURE"):
            return {"status": "FAILED", "transaction_id": transaction_id}
        if state in ("P", "PENDING", "PROCESSING"):
            return {"status": "PENDING", "transaction_id": transaction_id}
        if state not in ("S", "SUCCESS", "SUCCESSFUL"):
            return {"status": "UNKNOWN"}
        if (
            amount is None
            or Decimal(str(amount)) != execution.amount
            or str(recipient).lstrip("+") != execution.recipient_msisdn.lstrip("+")
        ):
            return {"status": "UNKNOWN"}
        return {
            "status": "SUCCESS",
            "reference": execution.reference,
            "amount": str(execution.amount),
            "currency": execution.currency,
            "recipient_msisdn": execution.recipient_msisdn,
            "transaction_id": transaction_id,
        }
