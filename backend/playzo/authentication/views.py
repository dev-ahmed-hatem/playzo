from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenVerifySerializer

from users.serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError(_("Username and password are required."))

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(_("Invalid username or password."))

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "player_id": user.player.id if hasattr(user, "player") else None,
            "username": user.username,
        }


class LoginView(APIView):
    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": _("Invalid username or password")}, status=status.HTTP_400_BAD_REQUEST)

        tokens = serializer.save()

        return Response(tokens, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Accepts a refresh token and returns a new access token.
    """
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CustomTokenVerifyView(TokenVerifyView):
    """
    Accepts a token and verifies if it is valid.
    """
    permission_classes = [AllowAny]
    serializer_class = TokenVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Token is invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"detail": "Token is valid"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_authenticated_user(request):
    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        user_serialized = UserSerializer(request.user, context={"request": request}).data
        return Response(user_serialized, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_401_UNAUTHORIZED)
