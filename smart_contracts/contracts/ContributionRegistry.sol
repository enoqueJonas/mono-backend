// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract ContributionRegistry {
    struct ContributionAnchor {
        bytes32 contributionHash;
        uint256 anchoredAt;
        address anchoredBy;
        bool exists;
    }

    mapping(bytes32 => ContributionAnchor) private anchors;

    event ContributionAnchored(
        bytes32 indexed contributionId,
        bytes32 indexed contributionHash,
        uint256 anchoredAt,
        address anchoredBy
    );

    function registerContribution(
        bytes32 contributionId,
        bytes32 contributionHash
    ) external {
        require(contributionId != bytes32(0), "Invalid contribution ID");
        require(contributionHash != bytes32(0), "Invalid contribution hash");
        require(!anchors[contributionId].exists, "Contribution already anchored");

        anchors[contributionId] = ContributionAnchor({
            contributionHash: contributionHash,
            anchoredAt: block.timestamp,
            anchoredBy: msg.sender,
            exists: true
        });

        emit ContributionAnchored(
            contributionId,
            contributionHash,
            block.timestamp,
            msg.sender
        );
    }

    function getContribution(
        bytes32 contributionId
    ) external view returns (
        bytes32 contributionHash,
        uint256 anchoredAt,
        address anchoredBy,
        bool exists
    ) {
        ContributionAnchor memory anchor = anchors[contributionId];

        return (
            anchor.contributionHash,
            anchor.anchoredAt,
            anchor.anchoredBy,
            anchor.exists
        );
    }

    function contributionExists(
        bytes32 contributionId
    ) external view returns (bool) {
        return anchors[contributionId].exists;
    }
}
