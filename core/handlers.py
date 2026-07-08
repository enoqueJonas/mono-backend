from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import DomainException


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, DomainException):
        return Response(
            {
                "message": exc.message
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "An unexpected error occurred."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
