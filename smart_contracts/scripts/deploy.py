from pathlib import Path
import shutil

from brownie import (
    ContributionRegistry,
    CredentialRegistry,
    GroupRegistry,
    accounts,
    network,
    config,
)


SMART_CONTRACTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SMART_CONTRACTS_DIR.parent


def _copy_backend_abi(contract_name: str):
    source = (
        SMART_CONTRACTS_DIR
        / "build"
        / "contracts"
        / f"{contract_name}.json"
    )
    destination = (
        PROJECT_ROOT
        / "blockchain"
        / "abi"
        / f"{contract_name}.json"
    )
    shutil.copy2(source, destination)


def _update_backend_env(
    *,
    credential_registry_address: str,
    group_registry_address: str,
    contribution_registry_address: str,
):
    env_file = PROJECT_ROOT / ".env"
    lines = env_file.read_text().splitlines()

    values = {
        "CREDENTIAL_REGISTRY_ADDRESS": credential_registry_address,
        "GROUP_REGISTRY_ADDRESS": group_registry_address,
        "CONTRIBUTION_REGISTRY_ADDRESS": contribution_registry_address,
    }

    updated_keys = set()
    updated_lines = []

    for line in lines:
        replaced = False
        for key, value in values.items():
            if line.startswith(f"{key}="):
                updated_lines.append(f"{key}={value}")
                updated_keys.add(key)
                replaced = True
                break
        if not replaced:
            updated_lines.append(line)

    for key, value in values.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}")

    env_file.write_text("\n".join(updated_lines) + "\n")


def get_account():
    if network.show_active() == "development":
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def main():
    account = get_account()

    credential_registry = CredentialRegistry.deploy({"from": account})
    group_registry = GroupRegistry.deploy({"from": account})
    contribution_registry = ContributionRegistry.deploy({"from": account})

    try:
        _copy_backend_abi("CredentialRegistry")
        _copy_backend_abi("GroupRegistry")
        _copy_backend_abi("ContributionRegistry")

        _update_backend_env(
            credential_registry_address=credential_registry.address,
            group_registry_address=group_registry.address,
            contribution_registry_address=contribution_registry.address,
        )

        print("✓ CredentialRegistry ABI copied")
        print("✓ GroupRegistry ABI copied")
        print("✓ ContributionRegistry ABI copied")
        print("✓ .env updated")
    except Exception as exc:
        print(f"⚠ Backend synchronization failed: {exc}")

    print("=" * 60)
    print("Contracts deployed successfully")
    print()
    print("CredentialRegistry")
    print(f"Address : {credential_registry.address}")
    print()
    print("GroupRegistry")
    print(f"Address : {group_registry.address}")
    print()
    print("ContributionRegistry")
    print(f"Address : {contribution_registry.address}")
    print()
    print("Backend updated")
    print("=" * 60)

    return {
        "credential_registry": credential_registry,
        "group_registry": group_registry,
        "contribution_registry": contribution_registry,
    }
