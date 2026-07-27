from __future__ import annotations

from typing import Any, Protocol

from blockchain.domain.blockchain_receipt import (
    BlockchainReceipt,
)


class BlockchainAnchorRepository(Protocol):
    def save(
        self,
        *,
        credential: Any,
        receipt: BlockchainReceipt,
    ):
        """Persist blockchain anchor."""
