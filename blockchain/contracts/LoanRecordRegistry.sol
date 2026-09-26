// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title LoanRecordRegistry
/// @notice Stores tamper-evident verification hashes for loan risk
///         assessment records produced by the LoanDefault MLBC academic
///         project. This contract intentionally stores NO sensitive
///         applicant information (no names, income, government IDs, bank
///         details, etc.) -- only a SHA-256 hash of a canonical record,
///         the risk category, and minimal bookkeeping fields required for
///         tamper-evidence and audit purposes.
contract LoanRecordRegistry {
    struct LoanRecord {
        string applicationId;
        bytes32 recordHash;
        string riskCategory;
        uint256 timestamp;
        address registrar;
        bool exists;
    }

    /// applicationId => LoanRecord
    mapping(string => LoanRecord) private records;

    /// Running count of registered records
    uint256 public totalRecords;

    address public owner;

    event LoanRecordRegistered(
        string indexed applicationIdIndexed,
        string applicationId,
        bytes32 recordHash,
        string riskCategory,
        uint256 timestamp,
        address indexed registrar
    );

    constructor() {
        owner = msg.sender;
    }

    /// @notice Registers a new loan record's hash on-chain.
    /// @dev Reverts if a record already exists for this applicationId --
    ///      registrations are immutable and cannot be overwritten.
    function registerRecord(
        string calldata applicationId,
        bytes32 recordHash,
        string calldata riskCategory
    ) external {
        require(bytes(applicationId).length > 0, "applicationId required");
        require(recordHash != bytes32(0), "recordHash required");
        require(!records[applicationId].exists, "Record already registered");

        records[applicationId] = LoanRecord({
            applicationId: applicationId,
            recordHash: recordHash,
            riskCategory: riskCategory,
            timestamp: block.timestamp,
            registrar: msg.sender,
            exists: true
        });

        totalRecords += 1;

        emit LoanRecordRegistered(
            applicationId,
            applicationId,
            recordHash,
            riskCategory,
            block.timestamp,
            msg.sender
        );
    }

    /// @notice Returns the full on-chain record for an applicationId.
    function getRecord(string calldata applicationId)
        external
        view
        returns (
            string memory applicationId_,
            bytes32 recordHash,
            string memory riskCategory,
            uint256 timestamp,
            address registrar
        )
    {
        require(records[applicationId].exists, "Record not found");
        LoanRecord storage r = records[applicationId];
        return (r.applicationId, r.recordHash, r.riskCategory, r.timestamp, r.registrar);
    }

    /// @notice Returns whether a record exists for the given applicationId.
    function recordExists(string calldata applicationId) external view returns (bool) {
        return records[applicationId].exists;
    }

    /// @notice Compares a freshly computed hash against the stored on-chain
    ///         hash for the given applicationId.
    function verifyRecord(string calldata applicationId, bytes32 currentHash)
        external
        view
        returns (bool verified)
    {
        require(records[applicationId].exists, "Record not found");
        return records[applicationId].recordHash == currentHash;
    }

    /// @notice Returns only the registration timestamp for a record.
    function getRecordTimestamp(string calldata applicationId) external view returns (uint256) {
        require(records[applicationId].exists, "Record not found");
        return records[applicationId].timestamp;
    }
}
