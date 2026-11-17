// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title DisbursementRegistry
/// @notice Records application approvals, simulated settlements and beneficiary
///         acknowledgments. No event proves an actual external bank transfer.
contract DisbursementRegistry {
    address public immutable operator;

    struct DisbursementProof {
        bytes32 authorizationHash;
        bytes32 settlementHash;
        uint64 authorizedAt;
        uint64 settledAt;
        bool authorized;
        bool settled;
    }

    mapping(bytes32 => DisbursementProof) private proofs;

    struct AcknowledgmentProof {
        bytes32 evidenceHash;
        uint64 acknowledgedAt;
        bool exists;
    }

    mapping(bytes32 => AcknowledgmentProof) private acknowledgments;

    event BeneficiaryAcknowledgmentRecorded(
        bytes32 indexed disbursementId, bytes32 indexed evidenceHash
    );

    event DisbursementAuthorized(bytes32 indexed disbursementId, bytes32 indexed authorizationHash);
    event DisbursementSettlementRecorded(bytes32 indexed disbursementId, bytes32 indexed settlementHash);

    constructor() {
        operator = msg.sender;
    }

    modifier onlyOperator() {
        require(msg.sender == operator, "Only authorized operator");
        _;
    }

    function recordAuthorization(
        bytes32 disbursementId,
        bytes32 authorizationHash
    ) external onlyOperator {
        require(disbursementId != bytes32(0), "Invalid disbursement ID");
        require(authorizationHash != bytes32(0), "Invalid authorization hash");
        DisbursementProof storage proof = proofs[disbursementId];
        require(!proof.authorized, "Authorization already recorded");

        proof.authorizationHash = authorizationHash;
        proof.authorizedAt = uint64(block.timestamp);
        proof.authorized = true;
        emit DisbursementAuthorized(disbursementId, authorizationHash);
    }

    /// @dev The backend must independently validate a signed provider settlement
    ///      before calling this function. The contract cannot validate bank funds.
    function recordSettlement(
        bytes32 disbursementId,
        bytes32 settlementHash
    ) external onlyOperator {
        require(settlementHash != bytes32(0), "Invalid settlement hash");
        DisbursementProof storage proof = proofs[disbursementId];
        require(proof.authorized, "Authorization not recorded");
        require(!proof.settled, "Settlement already recorded");

        proof.settlementHash = settlementHash;
        proof.settledAt = uint64(block.timestamp);
        proof.settled = true;
        emit DisbursementSettlementRecorded(disbursementId, settlementHash);
    }

    /// @notice App beneficiary acknowledges the custodian's claimed payment.
    ///         This is NOT a payment service provider confirmation.
    function recordBeneficiaryAcknowledgment(
        bytes32 disbursementId,
        bytes32 evidenceHash
    ) external onlyOperator {
        require(evidenceHash != bytes32(0), "Invalid acknowledgment hash");
        require(proofs[disbursementId].authorized, "Authorization not recorded");
        AcknowledgmentProof storage proof = acknowledgments[disbursementId];
        require(!proof.exists, "Acknowledgment already recorded");

        proof.evidenceHash = evidenceHash;
        proof.acknowledgedAt = uint64(block.timestamp);
        proof.exists = true;
        emit BeneficiaryAcknowledgmentRecorded(disbursementId, evidenceHash);
    }

    function getBeneficiaryAcknowledgment(bytes32 disbursementId)
        external view returns (bytes32 evidenceHash, uint64 acknowledgedAt, bool exists)
    {
        AcknowledgmentProof memory proof = acknowledgments[disbursementId];
        return (proof.evidenceHash, proof.acknowledgedAt, proof.exists);
    }

    function getDisbursement(bytes32 disbursementId)
        external view returns (
            bytes32 authorizationHash,
            bytes32 settlementHash,
            uint64 authorizedAt,
            uint64 settledAt,
            bool authorized,
            bool settled
        )
    {
        DisbursementProof memory proof = proofs[disbursementId];
        return (
            proof.authorizationHash,
            proof.settlementHash,
            proof.authorizedAt,
            proof.settledAt,
            proof.authorized,
            proof.settled
        );
    }
}
