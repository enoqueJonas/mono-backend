import pytest

from brownie import GroupRegistry, accounts, reverts


@pytest.fixture
def registry():
    return GroupRegistry.deploy(
        {
            "from": accounts[0],
        }
    )


def test_register_group_settings(registry):
    group_id = b"\x01" * 32
    settings_hash = b"\x02" * 32
    version = 1

    tx = registry.registerGroupSettings(
        group_id,
        version,
        settings_hash,
        {
            "from": accounts[0],
        },
    )

    result = registry.getGroupSettings(
        group_id,
        version,
    )

    assert bytes(result[0]) == settings_hash
    assert result[1] > 0
    assert result[2] == accounts[0]
    assert result[3] is True

    assert "GroupSettingsAnchored" in tx.events


def test_register_multiple_versions_for_same_group(
    registry,
):
    group_id = b"\x01" * 32

    registry.registerGroupSettings(
        group_id,
        1,
        b"\x02" * 32,
        {
            "from": accounts[0],
        },
    )

    registry.registerGroupSettings(
        group_id,
        2,
        b"\x03" * 32,
        {
            "from": accounts[0],
        },
    )

    version_1 = registry.getGroupSettings(
        group_id,
        1,
    )

    version_2 = registry.getGroupSettings(
        group_id,
        2,
    )

    assert bytes(version_1[0]) == b"\x02" * 32
    assert bytes(version_2[0]) == b"\x03" * 32

    assert version_1[3] is True
    assert version_2[3] is True


def test_cannot_register_same_version_twice(
    registry,
):
    group_id = b"\x01" * 32
    settings_hash = b"\x02" * 32

    registry.registerGroupSettings(
        group_id,
        1,
        settings_hash,
        {
            "from": accounts[0],
        },
    )

    with reverts(
        "Group settings already anchored"
    ):
        registry.registerGroupSettings(
            group_id,
            1,
            settings_hash,
            {
                "from": accounts[0],
            },
        )


def test_different_groups_can_have_same_version(
    registry,
):
    group_1 = b"\x01" * 32
    group_2 = b"\x02" * 32

    registry.registerGroupSettings(
        group_1,
        1,
        b"\x03" * 32,
        {
            "from": accounts[0],
        },
    )

    registry.registerGroupSettings(
        group_2,
        1,
        b"\x04" * 32,
        {
            "from": accounts[0],
        },
    )

    assert registry.groupSettingsExists(
        group_1,
        1,
    )

    assert registry.groupSettingsExists(
        group_2,
        1,
    )


def test_rejects_zero_version(registry):
    with reverts(
        "Invalid version"
    ):
        registry.registerGroupSettings(
            b"\x01" * 32,
            0,
            b"\x02" * 32,
            {
                "from": accounts[0],
            },
        )


def test_rejects_zero_group_id(registry):
    with reverts(
        "Invalid group ID"
    ):
        registry.registerGroupSettings(
            b"\x00" * 32,
            1,
            b"\x02" * 32,
            {
                "from": accounts[0],
            },
        )


def test_rejects_zero_settings_hash(registry):
    with reverts(
        "Invalid settings hash"
    ):
        registry.registerGroupSettings(
            b"\x01" * 32,
            1,
            b"\x00" * 32,
            {
                "from": accounts[0],
            },
        )
