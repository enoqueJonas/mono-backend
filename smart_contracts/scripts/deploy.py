from brownie import (
    CredentialRegistry,
    accounts,
    network,
    config,
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

    print("=" * 60)
    print("CredentialRegistry deployed")
    print(contract.address)
    print("=" * 60)

    return contract
