from django.db import transaction

from accounts.models import User
from core.exceptions import DomainException
from groups.models import Group
from identity.models import GroupDID, UserDID
from identity.utils.keys import generate_did_key_pair


class DIDAlreadyExists(DomainException):
    default_message = "The entity already has a decentralized identity."


class DIDNotFound(DomainException):
    default_message = "Decentralized identity not found."


class DIDService:
    @staticmethod
    @transaction.atomic
    def create_for_user(*, user: User) -> UserDID:
        if UserDID.objects.filter(user=user).exists():
            raise DIDAlreadyExists()

        generated = generate_did_key_pair()

        return UserDID.objects.create(
            user=user,
            method=UserDID.Method.KEY,
            did=generated.did,
            public_key_multibase=generated.public_key_multibase,
            encrypted_private_key=generated.encrypted_private_key,
            status=UserDID.Status.ACTIVE,
        )

    @staticmethod
    @transaction.atomic
    def create_for_group(*, group: Group) -> GroupDID:
        if GroupDID.objects.filter(group=group).exists():
            raise DIDAlreadyExists()

        generated = generate_did_key_pair()

        return GroupDID.objects.create(
            group=group,
            method=GroupDID.Method.KEY,
            did=generated.did,
            public_key_multibase=generated.public_key_multibase,
            encrypted_private_key=generated.encrypted_private_key,
            status=GroupDID.Status.ACTIVE,
        )

    @staticmethod
    def build_document(*, identity) -> dict:
        verification_method_id = identity.verification_method_id

        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/multikey/v1",
            ],
            "id": identity.did,
            "verificationMethod": [
                {
                    "id": verification_method_id,
                    "type": "Multikey",
                    "controller": identity.did,
                    "publicKeyMultibase": (
                        identity.public_key_multibase
                    ),
                }
            ],
            "authentication": [
                verification_method_id,
            ],
            "assertionMethod": [
                verification_method_id,
            ],
        }
