"""Actual Ganache signing and operator custody checks for all three registries.

Run after scripts/compile-contract-artifacts.mjs; never uses production keys.
This test is additional to the independent Brownie and Django/API test suites.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from uuid import uuid4

import pytest
from django.conf import settings
from web3 import Web3

from blockchain.clients.contribution_registry_client import ContributionRegistryClient
from blockchain.clients.credential_registry_client import CredentialRegistryClient
from blockchain.clients.group_registry_client import GroupRegistryClient
from blockchain.config.blockchain_config_factory import BlockchainConfigFactory
from blockchain.domain.blockchain_account import BlockchainAccount
from blockchain.domain.blockchain_config import BlockchainConfig
from blockchain.domain.credential_anchor_request import CredentialAnchorRequest

GANACHE_URL = os.environ.get("BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545")
ROOT = Path(__file__).resolve().parents[1]


def _node():
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL, request_kwargs={"timeout": 5}))
    for _ in range(30):
        if w3.is_connected():
            return w3
        time.sleep(1)
    pytest.fail("Ganache unavailable; the live custody test must not be skipped")


def _artifact(name):
    file = ROOT / "blockchain" / "abi" / f"{name}.json"
    source = ROOT / "smart_contracts" / "contracts" / f"{name}.sol"
    artifact = json.loads(file.read_text(encoding="utf-8"))
    assert artifact["contractName"] == name
    assert artifact["compilerVersion"].startswith("0.8.20+")
    assert artifact["sourceSha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert artifact["bytecode"].startswith("0x")
    assert any(x.get("name") == "operator" for x in artifact["abi"])
    return artifact


def _deploy(w3, artifact, from_address, private_key=None):
    factory = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
    if private_key is None:
        # The single known Ganache operator account is unlocked by the node.
        tx_hash = factory.constructor().transact({"from": from_address})
    else:
        # A newly created adversarial account is NOT unlocked by Ganache.
        # Deploy via an actual locally signed transaction, never eth_sendTransaction.
        tx = factory.constructor().build_transaction({
            "from": from_address,
            "nonce": w3.eth.get_transaction_count(from_address),
            "chainId": w3.eth.chain_id,
            "gasPrice": w3.eth.gas_price,
            "gas": 3_000_000,
        })
        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1
    return w3.eth.contract(address=receipt.contractAddress, abi=artifact["abi"])


def _reverted_outsider_tx(w3, function, account):
    # Fixed gas avoids Web3 attempting estimate_gas for a revert.
    tx = function.build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "chainId": w3.eth.chain_id,
        "gasPrice": w3.eth.gas_price,
        "gas": 250_000,
    })
    signed = w3.eth.account.sign_transaction(tx, account.key)
    receipt = w3.eth.wait_for_transaction_receipt(
        w3.eth.send_raw_transaction(signed.raw_transaction)
    )
    assert receipt.status == 0, "An outsider changed protected registry state"


@pytest.mark.parametrize(
    "name, client_type",
    [
        ("GroupRegistry", GroupRegistryClient),
        ("ContributionRegistry", ContributionRegistryClient),
        ("CredentialRegistry", CredentialRegistryClient),
    ],
)
def test_live_operator_custody_and_outsider_denial(name, client_type):
    w3 = _node()
    assert w3.eth.chain_id == 1337
    signer = w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
    assert signer.address == Web3.to_checksum_address(settings.BLOCKCHAIN_ACCOUNT_ADDRESS)
    assert signer.address == Web3.to_checksum_address(w3.eth.accounts[0])

    artifact = _artifact(name)
    contract = _deploy(w3, artifact, signer.address)
    assert Web3.to_checksum_address(contract.functions.operator().call()) == signer.address

    # Each client must pass chain/network/address/operator checks BEFORE signing.
    client = client_type(
        BlockchainConfigFactory.from_settings(contract_address=contract.address)
    )
    outsider = w3.eth.account.create()
    assert outsider.address != signer.address
    funding = w3.eth.send_transaction({
        "from": signer.address, "to": outsider.address,
        "value": w3.to_wei(1, "ether"),
    })
    assert w3.eth.wait_for_transaction_receipt(funding).status == 1

    if name == "GroupRegistry":
        group_id = str(uuid4())
        group_id32 = client._uuid_to_bytes32(group_id)
        settings_hash = "11" * 32
        _reverted_outsider_tx(
            w3,
            contract.functions.registerGroupSettings(
                group_id32, 1, bytes.fromhex(settings_hash)
            ),
            outsider,
        )
        assert contract.functions.groupSettingsExists(group_id32, 1).call() is False
        receipt = client.register_group_settings(
            group_id=group_id, version=1, settings_hash=settings_hash,
        )
        assert receipt.status
        stored = client.get_group_settings(group_id=group_id, version=1)
        assert stored["exists"] and stored["anchored_by"] == signer.address
        assert stored["settings_hash"] == settings_hash

    elif name == "ContributionRegistry":
        contribution_id = str(uuid4())
        contribution_id32 = client._uuid_to_bytes32(contribution_id)
        content_hash = "22" * 32
        _reverted_outsider_tx(
            w3,
            contract.functions.registerContribution(
                contribution_id32, bytes.fromhex(content_hash)
            ),
            outsider,
        )
        assert contract.functions.contributionExists(contribution_id32).call() is False
        receipt = client.register_contribution(
            contribution_id=contribution_id,
            contribution_hash=content_hash,
        )
        assert receipt.status
        stored = client.get_contribution(contribution_id)
        assert stored["exists"] and stored["anchored_by"] == signer.address
        assert stored["contribution_hash"] == content_hash

    else:
        content_hash = "33" * 32
        hash32 = bytes.fromhex(content_hash)
        _reverted_outsider_tx(
            w3, contract.functions.registerCredentialHash(hash32), outsider
        )
        assert contract.functions.credentialExists(hash32).call() is False
        receipt = client.register_credential_hash(
            CredentialAnchorRequest(credential_hash=content_hash)
        )
        assert receipt.status
        stored = client.get_credential(content_hash)
        assert stored["exists"] and stored["anchored_by"] == signer.address
        _reverted_outsider_tx(
            w3, contract.functions.revokeCredential(hash32), outsider
        )
        assert client.get_credential(content_hash)["revoked"] is False
        legitimate = client.revoke_credential(content_hash)
        assert legitimate.status
        assert client.get_credential(content_hash)["revoked"] is True

    print(f"REGISTRY_CUSTODY name={name} operator_matches_backend=True outsider_rejected=True signed_backend_write=True")


def test_client_refuses_foreign_operator_wrong_chain_and_no_contract():
    w3 = _node()
    signer = w3.eth.account.from_key(settings.BLOCKCHAIN_PRIVATE_KEY)
    outsider = w3.eth.account.create()
    fund = w3.eth.send_transaction({
        "from": signer.address, "to": outsider.address,
        "value": w3.to_wei(1, "ether"),
    })
    assert w3.eth.wait_for_transaction_receipt(fund).status == 1

    # The actual EVM contract is deployed by somebody OTHER than the backend.
    group_registry = _deploy(
        w3, _artifact("GroupRegistry"), outsider.address, private_key=outsider.key
    )
    base_cfg = BlockchainConfig(
        rpc_url=GANACHE_URL,
        chain_id=1337,
        contract_address=group_registry.address,
        account=BlockchainAccount(
            address=signer.address,
            private_key=settings.BLOCKCHAIN_PRIVATE_KEY,
        ),
    )
    with pytest.raises(ValueError, match="not the deployed registry operator"):
        GroupRegistryClient(base_cfg)

    wrong_chain_cfg = BlockchainConfig(
        rpc_url=GANACHE_URL, chain_id=1,
        contract_address=group_registry.address, account=base_cfg.account,
    )
    with pytest.raises(ValueError, match="chain ID differs"):
        GroupRegistryClient(wrong_chain_cfg)

    missing_contract_cfg = BlockchainConfig(
        rpc_url=GANACHE_URL, chain_id=1337,
        contract_address=outsider.address, account=base_cfg.account,
    )
    with pytest.raises(ValueError, match="no deployed EVM bytecode"):
        GroupRegistryClient(missing_contract_cfg)
    print("REGISTRY_CUSTODY negative_configs_rejected=True")
