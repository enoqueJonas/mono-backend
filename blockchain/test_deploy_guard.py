"""Tests for local Brownie deployment preflight; no actual node or keys used."""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from smart_contracts.scripts.deploy_guard import assert_deployer_matches_backend

TEST_KEY = "0x" + "0" * 63 + "1"
TEST_OPERATOR = "0x7E5F4552091A69125d5DfCb7b8C2659029395Bdf"
OTHER_OPERATOR = "0x0000000000000000000000000000000000000002"


def _env_file(directory, *, key=TEST_KEY, address=TEST_OPERATOR):
    target = Path(directory) / ".env"
    target.write_text(
        f'BLOCKCHAIN_PRIVATE_KEY="{key}"\nBLOCKCHAIN_ACCOUNT_ADDRESS={address}\n',
        encoding="utf-8",
    )
    return target


def test_preflight_accepts_matching_test_deployer():
    with TemporaryDirectory() as directory:
        assert_deployer_matches_backend(
            TEST_OPERATOR, _env_file(directory)
        )


def test_preflight_blocks_brownie_account_not_matching_backend():
    with TemporaryDirectory() as directory:
        with pytest.raises(RuntimeError, match="deployer differs") as exc:
            assert_deployer_matches_backend(
                OTHER_OPERATOR, _env_file(directory)
            )
        assert TEST_KEY not in str(exc.value)


def test_preflight_blocks_backend_address_not_matching_key():
    with TemporaryDirectory() as directory:
        with pytest.raises(RuntimeError, match="does not match"):
            assert_deployer_matches_backend(
                TEST_OPERATOR,
                _env_file(directory, address=OTHER_OPERATOR),
            )


def test_preflight_blocks_missing_or_incomplete_backend_env():
    with TemporaryDirectory() as directory:
        path = Path(directory) / ".env"
        with pytest.raises(RuntimeError, match="required"):
            assert_deployer_matches_backend(TEST_OPERATOR, path)
        path.write_text("BLOCKCHAIN_ACCOUNT_ADDRESS=" + TEST_OPERATOR + "\n")
        with pytest.raises(RuntimeError, match="not configured"):
            assert_deployer_matches_backend(TEST_OPERATOR, path)
