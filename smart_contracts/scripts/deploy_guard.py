"""Preflight guard for local Brownie deployment to a backend-managed test node.

This does not load production secret stores or deploy contracts. It validates
that the backend's actual signing key can operate the new operator-only
registries. Do not print or return private key material in error messages.
"""
from pathlib import Path

from eth_account import Account
from web3 import Web3


def _read_backend_env(file_path: Path) -> dict[str, str]:
    if not file_path.is_file():
        raise RuntimeError("Backend .env is required before registry deployment.")

    values = {}
    for line in file_path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#") or "=" not in item:
            continue
        key, value = item.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def assert_deployer_matches_backend(deployer_address: str, env_path: Path) -> None:
    values = _read_backend_env(env_path)
    private_key = values.get("BLOCKCHAIN_PRIVATE_KEY")
    declared_address = values.get("BLOCKCHAIN_ACCOUNT_ADDRESS")
    if not private_key or not declared_address:
        raise RuntimeError(
            "Backend signer key/address not configured in .env; refusing deployment."
        )

    try:
        key_address = Account.from_key(private_key).address
        configured_address = Web3.to_checksum_address(declared_address)
        actual_deployer = Web3.to_checksum_address(str(deployer_address))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Invalid backend EVM signer configuration.") from exc

    if key_address != configured_address:
        raise RuntimeError(
            "Backend EVM signing private key does not match the declared address."
        )
    if actual_deployer != key_address:
        raise RuntimeError(
            "Brownie deployer differs from the backend EVM signer. "
            "Refusing to deploy operator-only contracts with incompatible accounts."
        )
