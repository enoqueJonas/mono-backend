from django.db import transaction
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.exceptions import DomainException
from identity.services.did_service import DIDService


class InvalidCredentials(DomainException):

    default_message = "Invalid phone number or password."


class AuthService:

    @staticmethod
    @transaction.atomic
    def register(data: dict) -> User:
        """
        Register a new user.
        """

        password = data.pop("password")
        data.pop("confirm_password", None)

        user = User.objects.create_user(
            password=password,
            **data,
        )

        DIDService.create_for_user(user=user)

        return user

    @staticmethod
    def login(data: dict) -> dict:
        user = authenticate(
            phone_number=data["phone_number"],
            password=data["password"],
        )

        if user is None:
            raise InvalidCredentials()

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }
