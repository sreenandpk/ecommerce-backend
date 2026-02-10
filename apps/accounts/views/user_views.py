from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.accounts.serializers import UserProfileSerializer


# ============================
# CURRENT USER
# ============================
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ ADD THIS LINE (SAFE)
        request.user.recently_viewed.set(
            request.user.recently_viewed.all()
        )

        serializer = UserProfileSerializer(
            request.user,
            context={"request": request}
        )
        return Response(serializer.data)

# ============================
# PROFILE GET / UPDATE
# ============================
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        # ✅ ADD THIS LINE
        request.user.recently_viewed.set(
            request.user.recently_viewed.all()
        )

        serializer = UserProfileSerializer(
            request.user,
            context={"request": request}
        )
        return Response(serializer.data)

    def patch(self, request):
        # ✅ ADD THIS LINE
        request.user.recently_viewed.set(
            request.user.recently_viewed.all()
        )

        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
