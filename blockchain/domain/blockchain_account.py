from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlockchainAccount:
    """
    Represents the account used to sign blockchain transactions.
    """

    address: str
    private_key: str
