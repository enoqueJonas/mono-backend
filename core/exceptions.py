class DomainException(Exception):

    default_message = "Operation failed."

    def __init__(self, message=None):

        self.message = message or self.default_message

        super().__init__(self.message)


class UserAlreadyExists(DomainException):

    default_message = "User already exists."


class InvalidContribution(DomainException):

    default_message = "Contribution is invalid."


class GroupClosed(DomainException):

    default_message = "Group is closed."
