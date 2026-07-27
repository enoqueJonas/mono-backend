from pathlib import Path
import json
import shutil
from brownie import (
    CredentialRegistry,
    accounts,
    network,
    config,
)

SMART_CONTRACTS_DIR = Path(__file__).resolve().parents[1]

PROJECT_ROOT = SMART_CONTRACTS_DIR.parent


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _copy_backend_abi():

    source = (
        SMART_CONTRACTS_DIR
        / "build"
        / "contracts"
        / "CredentialRegistry.json"

    )

    destination = (
        PROJECT_ROOT
        / "blockchain"
        / "abi"
        / "CredentialRegistry.json"
    )

    shutil.copy2(source, destination)


def _update_backend_env(address: str):
    env_file = PROJECT_ROOT / ".env"

    lines = env_file.read_text().splitlines()

    updated_lines = []

    updated = False

    for line in lines:

        if line.startswith(
            "CREDENTIAL_REGISTRY_ADDRESS="
        ):
            updated_lines.append(
                f"CREDENTIAL_REGISTRY_ADDRESS={address}"
            )
            updated = True

        else:
            updated_lines.append(line)

    if not updated:
        updated_lines.append(
            f"CREDENTIAL_REGISTRY_ADDRESS={address}"
        )

    env_file.write_text(
        "\n".join(updated_lines) + "\n"
    )


def get_account():
    if network.show_active() == "development":
        return accounts[0]

    return accounts.add(
        config["wallets"]["from_key"]
    )


def main():

    account = get_account()
    contract = CredentialRegistry.deploy(
        {
            "from": account,
        }
    )

    try:
        _copy_backend_abi()
        _update_backend_env(contract.address)
        print("✓ ABI copied")
        print("✓ .env updated")

    except Exception as e:
        print(f"⚠ Backend synchronization failed: {e}")

    print("=" * 60)
    print("CredentialRegistry deployed successfully")
    print()
    print(f"Address : {contract.address}")
    print()
    print("Backend updated")
    print("✓ ABI copied")
    print("✓ .env updated")
    print("=" * 60)

    return contract
