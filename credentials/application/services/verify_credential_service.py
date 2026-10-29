"""Verify authenticity, validity and on-chain revocation of a locally issued VC."""
from datetime import datetime, timedelta, timezone

from blockchain.services.anchor_service import AnchorService
from blockchain.utils.hashing import HashingService
from credentials.domain.value_objects import CredentialHash
from credentials.services.credential_signer import CredentialSigner
from identity.models import GroupDID


class VerifyCredentialService:
    # Small tolerance for clock skew on newly issued credentials.
    MAX_CLOCK_SKEW = timedelta(minutes=5)

    def __init__(
        self,
        *,
        anchor_service: AnchorService | None = None,
        signer=None,
        issuer_lookup=None,
    ) -> None:
        # Do not connect to a blockchain for an obviously malformed credential.
        self.anchor_service = anchor_service
        self.signer = signer or CredentialSigner()
        self.issuer_lookup = issuer_lookup or self._resolve_issuer

    @staticmethod
    def _resolve_issuer(did: str):
        return GroupDID.objects.filter(
            did=did,
            status=GroupDID.Status.ACTIVE,
        ).first()

    @staticmethod
    def _parse_timestamp(value):
        if not isinstance(value, str):
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc)

    def verify(self, *, credential: dict) -> bool:
        if not isinstance(credential, dict):
            return False
        issuer_did = credential.get("issuer")
        subject = credential.get("credentialSubject")
        proof = credential.get("proof")
        if (
            not isinstance(issuer_did, str)
            or not issuer_did
            or not isinstance(subject, dict)
            or not isinstance(proof, dict)
        ):
            return False

        issued_at = self._parse_timestamp(credential.get("issuanceDate"))
        valid_until = self._parse_timestamp(credential.get("validUntil"))
        proof_created = self._parse_timestamp(proof.get("created"))
        now = datetime.now(timezone.utc)
        if (
            issued_at is None
            or valid_until is None
            or proof_created is None
            or issued_at > now + self.MAX_CLOCK_SKEW
            or now >= valid_until
            or valid_until <= issued_at
            or abs((proof_created - issued_at).total_seconds()) >= 1
        ):
            return False

        identity = self.issuer_lookup(issuer_did)
        if identity is None:
            return False
        if not self.signer.verify(
            signed_document=credential,
            issuer_identity=identity,
        ):
            return False

        try:
            credential_hash = CredentialHash(
                value=HashingService.hash_json_hex(credential)
            )
        except (TypeError, ValueError, OverflowError):
            return False

        anchor_service = self.anchor_service or AnchorService()
        if not anchor_service.credential_exists(
            credential_hash=credential_hash
        ):
            return False
        state = anchor_service.get_credential(
            credential_hash=credential_hash
        )
        return bool(state.get("exists") and not state.get("revoked"))
