"""Fail-closed runtime checks for the three operator-only registry contracts.

Ensures that a Django signer is communicating with an EVM contract that actually
enforces the configured operator address. This does NOT establish code
provenance, self-custody, multisig, or payment-provider authorization.
"""
from web3 import Web3


def require_registry_operator(*, web3, contract, config) -> None:
    current_chain = int(web3.eth.chain_id)
    if current_chain != int(config.chain_id):
        raise ValueError(
            "Blockchain RPC chain ID differs from BLOCKCHAIN_CHAIN_ID. "
            "Refusing contract operations."
        )

    if not web3.eth.get_code(contract.address):
        raise ValueError(
            "Registry address contains no deployed EVM bytecode. "
            "Check the contract deployment and configured address."
        )

    try:
        deployed_operator = Web3.to_checksum_address(
            contract.functions.operator().call()
        )
    except Exception as exc:
        raise ValueError(
            "Registry operator() is unavailable. "
            "Refusing an outdated ABI or incompatible deployed contract."
        ) from exc

    configured_signer = Web3.to_checksum_address(config.account.address)
    if deployed_operator != configured_signer:
        raise ValueError(
            "Configured backend signer is not the deployed registry operator. "
            "Redeploy consistently or configure the authorized test signer."
        )
