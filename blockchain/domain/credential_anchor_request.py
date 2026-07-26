from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CredentialAnchorRequest:
    credential_hash: bytes

    def __post_init__(self) -> None:
        if len(self.credential_hash) != 32:
            raise ValueError(
                "Credential hash must contain exactly 32 bytes."
            )
