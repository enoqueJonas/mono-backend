from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    reason: str | None = None

    @classmethod
    def allow(cls) -> "PolicyDecision":
        return cls(
            allowed=True,
            reason=None,
        )

    @classmethod
    def deny(cls, reason: str) -> "PolicyDecision":
        if not reason.strip():
            raise ValueError(
                "Policy denial reason cannot be empty."
            )

        return cls(
            allowed=False,
            reason=reason,
        )
