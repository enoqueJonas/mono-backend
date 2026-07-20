import json
from pathlib import Path
from typing import Any

from django.conf import settings
from web3 import Web3
from web3.contract import Contract

from blockchain.exceptions import (
    BlockchainConnectionError,
    ContractNotDeployedError,
    InvalidContractAddressError,
)


class CredentialRegistryClient:
    def __init__(
        self,
        rpc_url: str | None = None,
        contract_address: str | None = None,
    ) -> None:
        self.rpc_url = (
            rpc_url
            or settings.BLOCKCHAIN_RPC_URL
        )

        self.contract_address = (
            contract_address
            or settings.CREDENTIAL_REGISTRY_ADDRESS
        )

        self.web3 = Web3(
            Web3.HTTPProvider(self.rpc_url)
        )

        self._validate_connection()
        self.contract = self._build_contract()

    def _validate_connection(self) -> None:
        if not self.web3.is_connected():
            raise BlockchainConnectionError(
                f"Unable to connect to blockchain RPC: "
                f"{self.rpc_url}"
            )

    def _build_contract(self) -> Contract:
        if not Web3.is_address(
            self.contract_address
        ):
            raise InvalidContractAddressError(
                "CREDENTIAL_REGISTRY_ADDRESS is invalid."
            )

        checksum_address = Web3.to_checksum_address(
            self.contract_address
        )

        contract_code = self.web3.eth.get_code(
            checksum_address
        )

        if contract_code in (b"", b"\x00"):
            raise ContractNotDeployedError(
                "No contract code was found at "
                f"{checksum_address}."
            )

        return self.web3.eth.contract(
            address=checksum_address,
            abi=self._load_abi(),
        )

    @staticmethod
    def _load_abi() -> list[dict[str, Any]]:
        abi_path = (
            Path(__file__).resolve().parent.parent
            / "abi"
            / "CredentialRegistry.json"
        )

        with abi_path.open(
            "r",
            encoding="utf-8",
        ) as abi_file:
            return json.load(abi_file)

    def credential_exists(
        self,
        credential_hash: bytes,
    ) -> bool:
        self._validate_hash(credential_hash)

        return bool(
            self.contract.functions
            .credentialExists(credential_hash)
            .call()
        )

    def get_credential(
        self,
        credential_hash: bytes,
    ) -> dict[str, Any]:
        self._validate_hash(credential_hash)

        (
            exists,
            revoked,
            anchored_at,
            anchored_by,
        ) = (
            self.contract.functions
            .getCredential(credential_hash)
            .call()
        )

        return {
            "exists": exists,
            "revoked": revoked,
            "anchored_at": anchored_at,
            "anchored_by": anchored_by,
        }

    @staticmethod
    def _validate_hash(
        credential_hash: bytes,
    ) -> None:
        if not isinstance(
            credential_hash,
            bytes,
        ):
            raise TypeError(
                "Credential hash must be bytes."
            )

        if len(credential_hash) != 32:
            raise ValueError(
                "Credential hash must contain exactly "
                "32 bytes."
            )
