"""Document the implemented DID custody model as executable tests.

The server can decrypt DID private keys; this is a deliberately centralized
prototype, not self-sovereign key custody by individual Xitique members.
"""
import base58
from cryptography.fernet import Fernet
from django.test import TestCase, override_settings
from nacl.signing import SigningKey

from accounts.models import User
from groups.models import Group
from identity.services.did_service import DIDService
from identity.utils.keys import (
    DIDKeyEncryptionError,
    decrypt_private_key,
)


class DIDCustodyBoundaryTests(TestCase):
    def test_user_did_private_key_is_server_decryptable_not_exposed_in_document(self):
        person = User.objects.create_user(
            phone_number="+258841996101",
            password="synthetic-credentials",
        )
        identity = DIDService.create_for_user(user=person)
        private_key = decrypt_private_key(identity.encrypted_private_key)
        assert len(private_key) == 32

        # The public multicodec key matches the server-decrypted private key.
        public_multicodec = base58.b58decode(identity.public_key_multibase[1:])
        assert public_multicodec[:2] == bytes([0xED, 0x01])
        assert public_multicodec[2:] == SigningKey(private_key).verify_key.encode()

        document = DIDService.build_document(identity=identity)
        assert document["id"] == identity.did
        assert "encrypted_private_key" not in document
        assert "privateKeyMultibase" not in str(document)
        assert identity.encrypted_private_key not in str(document)

    def test_group_issuer_key_is_held_by_application_not_members(self):
        group = Group.objects.create(name="Grupo chave institucional de teste")
        identity = DIDService.create_for_group(group=group)
        private_key = decrypt_private_key(identity.encrypted_private_key)
        assert len(private_key) == 32
        assert SigningKey(private_key).verify_key.encode() == (
            base58.b58decode(identity.public_key_multibase[1:])[2:]
        )

    def test_key_material_cannot_be_decrypted_with_an_unrelated_server_key(self):
        person = User.objects.create_user(
            phone_number="+258841996102",
            password="synthetic-credentials",
        )
        identity = DIDService.create_for_user(user=person)
        with override_settings(DID_KEY_ENCRYPTION_KEY=Fernet.generate_key().decode()):
            with self.assertRaises(DIDKeyEncryptionError):
                decrypt_private_key(identity.encrypted_private_key)
