from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Protocol


class ContributionLike(Protocol):
    amount: Decimal
    currency: str
    status: str
    contribution_period: date
    reference: str
