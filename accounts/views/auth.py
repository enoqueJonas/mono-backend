from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.register import RegisterSerializer
from accounts.serializers.profile import ProfileSerializer
from accounts.services.auth_service import AuthService
from accounts.serializers.login import LoginSerializer
from core.responses import success


class RegisterView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = AuthService.register(
            serializer.validated_data
        )

        return Response(
            ProfileSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AuthService.login(serializer.validated_data)

        return success(
            data={
                "access": result["access"],
                "refresh": result["refresh"],
                "user": ProfileSerializer(result["user"]).data,
            }
        )
