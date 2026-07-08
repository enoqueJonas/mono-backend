from rest_framework import status
from rest_framework.response import Response


def success(data=None, message=None, status_code=status.HTTP_200_OK):

    payload = {}

    if message:
        payload["message"] = message

    if data is not None:
        payload["data"] = data

    return Response(payload, status=status_code)
