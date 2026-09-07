from pathlib import Path
import shutil

from brownie import ContributionRegistry, accounts, config, network


SMART_CONTRACTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SMART_CONTRACTS_DIR.parent


def get_account():
    if network.show_active() == "development":
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def _copy_backend_abi():
    source = (
        SMART_CONTRACTS_DIR
        / "build"
        / "contracts"
        / "ContributionRegistry.json"
    )
    destination = (
        PROJECT_ROOT
        / "blockchain"
        / "abi"
        / "ContributionRegistry.json"
    )
    shutil.copy2(source, destination)


def _update_backend_env(contract_address: str):
    env_file = PROJECT_ROOT / ".env"
    lines = env_file.read_text().splitlines()
    key = "CONTRIBUTION_REGISTRY_ADDRESS"
    updated = False
    output = []

    for line in lines:
        if line.startswith(f"{key}="):
            output.append(f"{key}={contract_address}")
            updated = True
        else:
            output.append(line)

    if not updated:
        output.append(f"{key}={contract_address}")

    env_file.write_text("\n".join(output) + "\n")


def main():
    account = get_account()
    registry = ContributionRegistry.deploy({"from": account})

    _copy_backend_abi()
    _update_backend_env(registry.address)

    print("=" * 60)
    print("ContributionRegistry deployed successfully")
    print(f"Address : {registry.address}")
    print("✓ ContributionRegistry ABI copied")
    print("✓ .env updated")
    print("=" * 60)

    return registry
