from blockchain.utils.hashing import HashingService

from credentials.domain.value_objects import (
    CredentialDocument,
    CredentialHash,
)


class CredentialHashService:
    def calculate(
        self,
        document: CredentialDocument,
    ) -> CredentialHash:
        return CredentialHash(
            value=HashingService.hash_json_hex(
                document.to_dict()
            )
        )
