from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerReadSerializer, PlayerWriteSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PlayerWriteSerializer
        return PlayerReadSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            player = request.user.player
            serializer = self.get_serializer(player)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
