import traceback
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import DomainException, PermissionDomainException


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        return response

    if isinstance(exc, DomainException):
        return Response(
            {
                "message": exc.message
            },
            status=(
                status.HTTP_403_FORBIDDEN
                if isinstance(exc, PermissionDomainException)
                else status.HTTP_400_BAD_REQUEST
            ),
        )
    traceback.print_exc()
    return Response(
        {
            "message": "An unexpected error occurred."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
