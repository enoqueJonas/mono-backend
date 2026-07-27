from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CredentialAnchorRequest:
    credential_hash: str

    def __post_init__(self) -> None:
        if len(self.credential_hash) != 64:
            raise ValueError(
                "Credential hash must be a 64-character SHA-256 hexadecimal string."
            )
