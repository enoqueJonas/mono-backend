"""Regression tests documenting the custody boundary of the research prototype.

Passing these tests does not prove self-sovereign key custody. It proves the
opposite: the Django application can recover the group signing key and sign
a document without a member device or a member-held cryptographic key.
"""
from django.test import TestCase
from nacl.signing import SigningKey

from accounts.models import User
from credentials.services.credential_signer import CredentialSigner
from groups.models import Group
from identity.services.did_service import DIDService
from identity.utils.keys import decrypt_private_key


class CentralizedDIDKeyCustodyTests(TestCase):
    def test_group_key_is_encrypted_at_rest_but_recoverable_by_backend(self):
        group = Group.objects.create(name="Grupo com chave em custódia")
        identity = DIDService.create_for_group(group=group)

        private_key_bytes = decrypt_private_key(identity.encrypted_private_key)
        self.assertEqual(len(private_key_bytes), 32)
        self.assertNotEqual(identity.encrypted_private_key, private_key_bytes.hex())

        signing_key = SigningKey(private_key_bytes)
        self.assertEqual(
            signing_key.verify_key.encode(),
            CredentialSigner._build_verify_key(
                public_key_multibase=identity.public_key_multibase
            ).encode(),
        )

    def test_server_can_sign_group_credential_without_member_signature(self):
        group = Group.objects.create(name="Grupo emissor controlado pelo servidor")
        identity = DIDService.create_for_group(group=group)
        sample = {
            "id": "urn:uuid:11111111-1111-4111-8111-111111111111",
            "type": ["VerifiableCredential"],
            "issuer": identity.did,
            "credentialSubject": {"id": "did:example:synthetic-holder"},
        }

        signed = CredentialSigner.sign(
            document=sample,
            issuer_identity=identity,
        )
        self.assertTrue(
            CredentialSigner.verify(
                signed_document=signed.document,
                issuer_identity=identity,
            )
        )
        self.assertIn("proof", signed.document)
        self.assertEqual(signed.document["issuer"], identity.did)

        # No participant wallet, user-held signing key, or authenticated
        # member was involved. Do not claim SSI self-custody as a result.

    def test_user_did_private_key_is_also_recoverable_by_server(self):
        user = User.objects.create_user(
            phone_number="+258841890051",
            password="synthetic-only-test-password",
        )
        identity = DIDService.create_for_user(user=user)
        self.assertEqual(
            len(decrypt_private_key(identity.encrypted_private_key)),
            32,
        )
