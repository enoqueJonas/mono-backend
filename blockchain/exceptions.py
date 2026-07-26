class BlockchainError(Exception):
    """Base exception for blockchain integration errors."""


class InvalidContractAddressError(BlockchainError):
    """Raised when the configured contract address is invalid."""


class ContractNotDeployedError(BlockchainError):
    """Raised when there is no contract code at the configured address."""


class BlockchainException(Exception):
    """Base exception for blockchain infrastructure errors."""


class BlockchainConnectionError(BlockchainException):
    """Raised when the blockchain node cannot be reached."""


class TransactionFailed(BlockchainException):
    """Raised when a blockchain transaction fails or is reverted."""


class CredentialAlreadyAnchored(BlockchainException):
    """Raised when a credential hash is already anchored."""
