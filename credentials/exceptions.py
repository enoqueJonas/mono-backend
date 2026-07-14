from core.exceptions import DomainException


class InvalidCredentialPeriod(DomainException):
    default_message = (
        "The credential end period must be equal to or later "
        "than the start period."
    )


class NoConfirmedContributions(DomainException):
    default_message = (
        "No confirmed contributions were found for the selected period."
    )


class InactiveCredentialHolder(DomainException):
    default_message = (
        "Credentials can only be issued to active group members."
    )


class MissingIssuerDID(DomainException):
    default_message = (
        "The group does not have an issuer decentralized identity."
    )


class MissingHolderDID(DomainException):
    default_message = (
        "The member does not have a decentralized identity."
    )


class NotCredentialIssuer(DomainException):
    default_message = (
        "Only an active group manager can issue credentials."
    )


class CredentialAlreadyExists(DomainException):
    default_message = (
        "An active credential already exists for this member "
        "and period."
    )


class CredentialSignatureFailed(DomainException):
    default_message = (
        "The credential signature could not be verified."
    )


class CredentialNotFound(DomainException):
    default_message = "Credential not found."


class CredentialHolderNotFound(DomainException):
    default_message = (
        "The selected group member was not found."
    )
