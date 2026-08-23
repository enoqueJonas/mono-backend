// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract GroupRegistry {
    struct GroupSettingsAnchor {
        bytes32 settingsHash;
        uint256 version;
        uint256 anchoredAt;
        address anchoredBy;
        bool exists;
    }

    mapping(bytes32 => mapping(uint256 => GroupSettingsAnchor)) private anchors;

    event GroupSettingsAnchored(
        bytes32 indexed groupId,
        uint256 indexed version,
        bytes32 indexed settingsHash,
        uint256 anchoredAt,
        address anchoredBy
    );

    function registerGroupSettings(
        bytes32 groupId,
        uint256 version,
        bytes32 settingsHash
    ) external {
        require(groupId != bytes32(0), "Invalid group ID");

        require(version > 0, "Invalid version");

        require(settingsHash != bytes32(0), "Invalid settings hash");

        require(
            !anchors[groupId][version].exists,
            "Group settings already anchored"
        );

        anchors[groupId][version] = GroupSettingsAnchor({
            settingsHash: settingsHash,
            version: version,
            anchoredAt: block.timestamp,
            anchoredBy: msg.sender,
            exists: true
        });

        emit GroupSettingsAnchored(
            groupId,
            version,
            settingsHash,
            block.timestamp,
            msg.sender
        );
    }

    function getGroupSettings(
        bytes32 groupId,
        uint256 version
    )
        external
        view
        returns (
            bytes32 settingsHash,
            uint256 anchoredAt,
            address anchoredBy,
            bool exists
        )
    {
        GroupSettingsAnchor memory anchor = anchors[groupId][version];

        return (
            anchor.settingsHash,
            anchor.anchoredAt,
            anchor.anchoredBy,
            anchor.exists
        );
    }

    function groupSettingsExists(
        bytes32 groupId,
        uint256 version
    ) external view returns (bool) {
        return anchors[groupId][version].exists;
    }
}
