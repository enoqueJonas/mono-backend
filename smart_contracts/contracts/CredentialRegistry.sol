// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

contract CredentialRegistry {
    struct CredentialAnchor {
        bool exists;
        bool revoked;
        uint64 anchoredAt;
        address anchoredBy;
    }

    // A single test-network backend operator submits anchor/revocation transactions.
    // This is a defensive authorization boundary, not distributed governance.
    address public immutable operator;

    constructor() {
        operator = msg.sender;
    }

    modifier onlyOperator() {
        require(msg.sender == operator, "Only authorized operator");
        _;
    }

    mapping(bytes32 => CredentialAnchor) private anchors;

    event CredentialAnchored(
        bytes32 indexed credentialHash,
        address indexed anchoredBy
    );

    event CredentialRevoked(
        bytes32 indexed credentialHash,
        address indexed revokedBy
    );

    error CredentialAlreadyAnchored();
    error CredentialNotFound();
    error CredentialAlreadyRevoked();

    function registerCredentialHash(bytes32 credentialHash) external onlyOperator {
        if (anchors[credentialHash].exists) {
            revert CredentialAlreadyAnchored();
        }

        anchors[credentialHash] = CredentialAnchor({
            exists: true,
            revoked: false,
            anchoredAt: uint64(block.timestamp),
            anchoredBy: msg.sender
        });

        emit CredentialAnchored(credentialHash, msg.sender);
    }

    function revokeCredential(bytes32 credentialHash) external onlyOperator {
        CredentialAnchor storage anchor = anchors[credentialHash];

        if (!anchor.exists) {
            revert CredentialNotFound();
        }

        if (anchor.revoked) {
            revert CredentialAlreadyRevoked();
        }

        anchor.revoked = true;

        emit CredentialRevoked(credentialHash, msg.sender);
    }

    function credentialExists(
        bytes32 credentialHash
    ) external view returns (bool) {
        return anchors[credentialHash].exists;
    }

    function getCredential(
        bytes32 credentialHash
    )
        external
        view
        returns (
            bool exists,
            bool revoked,
            uint64 anchoredAt,
            address anchoredBy
        )
    {
        CredentialAnchor memory anchor = anchors[credentialHash];

        if (!anchor.exists) {
            revert CredentialNotFound();
        }

        return (
            anchor.exists,
            anchor.revoked,
            anchor.anchoredAt,
            anchor.anchoredBy
        );
    }
}
