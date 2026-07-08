from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.serializers.profile import ProfileSerializer
from core.responses import success


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success(
            data=ProfileSerializer(request.user).data
        )
