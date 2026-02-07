from django.db import transaction
from django.conf import settings

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    AdminUserSerializer,  # ✅ ADDED
)

# ============================
# REGISTER
# ============================
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "user": AdminUserSerializer(user).data,  # ✅ FIXED
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )

        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax" if settings.DEBUG else "None",
            path="/",
        )

        return response


# ============================
# LOGIN
# ============================
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "user": AdminUserSerializer(user).data,  # ✅ FIXED
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="refresh",
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax" if settings.DEBUG else "None",
            path="/",
        )

        return response


# ============================
# REFRESH TOKEN
# ============================
class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token

            return Response(
                {"access": str(access_token)},
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# ============================
# LOGOUT
# ============================
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")
        
        response = Response(
            {"detail": "Logged out"},
            status=status.HTTP_200_OK,
        )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass # Token might already be blacklisted or invalid

        response.delete_cookie("refresh", path="/")
        return response
