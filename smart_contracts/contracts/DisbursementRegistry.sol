// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Stores hashes of an approved payout intent and its verified result.
/// @dev This is evidence anchoring, NOT custody of funds or proof by itself that
///      a wallet operator settled a payment. Only the configured backend operator writes.
contract DisbursementRegistry {
    address public immutable operator;

    struct Proof {
        bytes32 intentHash;
        bytes32 settlementHash;
        uint64 intentAnchoredAt;
        uint64 settlementAnchoredAt;
    }

    mapping(bytes32 => Proof) private proofs;

    event IntentAnchored(bytes32 indexed disbursementId, bytes32 indexed intentHash);
    event SettlementAnchored(bytes32 indexed disbursementId, bytes32 indexed settlementHash);

    constructor() {
        operator = msg.sender;
    }

    modifier onlyOperator() {
        require(msg.sender == operator, "Only authorized operator");
        _;
    }

    function anchorIntent(bytes32 disbursementId, bytes32 intentHash) external onlyOperator {
        require(disbursementId != bytes32(0), "Invalid disbursement");
        require(intentHash != bytes32(0), "Invalid intent hash");
        require(proofs[disbursementId].intentAnchoredAt == 0, "Intent already anchored");
        proofs[disbursementId].intentHash = intentHash;
        proofs[disbursementId].intentAnchoredAt = uint64(block.timestamp);
        emit IntentAnchored(disbursementId, intentHash);
    }

    function anchorSettlement(bytes32 disbursementId, bytes32 settlementHash) external onlyOperator {
        require(settlementHash != bytes32(0), "Invalid settlement hash");
        require(proofs[disbursementId].intentAnchoredAt != 0, "Intent missing");
        require(proofs[disbursementId].settlementAnchoredAt == 0, "Settlement already anchored");
        proofs[disbursementId].settlementHash = settlementHash;
        proofs[disbursementId].settlementAnchoredAt = uint64(block.timestamp);
        emit SettlementAnchored(disbursementId, settlementHash);
    }

    function getProof(bytes32 disbursementId)
        external view returns (bytes32 intentHash, bytes32 settlementHash, uint64 intentAt, uint64 settlementAt)
    {
        Proof memory result = proofs[disbursementId];
        return (result.intentHash, result.settlementHash, result.intentAnchoredAt, result.settlementAnchoredAt);
    }
}
