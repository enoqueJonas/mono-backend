class BlockchainError(Exception):
    """Base exception for blockchain integration errors."""


class BlockchainConnectionError(BlockchainError):
    """Raised when the RPC node cannot be reached."""


class InvalidContractAddressError(BlockchainError):
    """Raised when the configured contract address is invalid."""


class ContractNotDeployedError(BlockchainError):
    """Raised when there is no contract code at the configured address."""
