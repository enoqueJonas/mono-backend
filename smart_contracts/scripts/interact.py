import hashlib
from brownie import CredentialRegistry, accounts, web3


CONTRACT_ADDRESS = (
    "0x7014b5D936193bF8A4086468E84390dFa657d1fD"
)


def main():
    account = accounts[0]

    registry = CredentialRegistry.at(
        CONTRACT_ADDRESS
    )

    credential_hash = hashlib.sha256(
        b"sample-verifiable-credential-001"
    ).digest()

    print("=" * 60)
    print("CredentialRegistry interaction")
    print(f"Contract: {registry.address}")
    print(f"Account: {account.address}")
    print(f"Hash: {web3.to_hex(credential_hash)}")
    print("=" * 60)

    already_exists = registry.credentialExists(
        credential_hash
    )

    if already_exists:
        print("Credential hash already anchored.")
    else:
        tx = registry.registerCredentialHash(
            credential_hash,
            {"from": account},
        )

        print("Credential anchored successfully.")
        print(f"Transaction hash: {tx.txid}")
        print(f"Block number: {tx.block_number}")

    (
        exists,
        revoked,
        anchored_at,
        anchored_by,
    ) = registry.getCredential(
        credential_hash
    )

    print()
    print("Stored credential:")
    print(f"Exists: {exists}")
    print(f"Revoked: {revoked}")
    print(f"Anchored at: {anchored_at}")
    print(f"Anchored by: {anchored_by}")
