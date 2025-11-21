from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Player
from .serializers import PlayerReadSerializer, PlayerWriteSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return PlayerWriteSerializer
        return PlayerReadSerializer

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        player = request.user.player
        serializer = self.get_serializer(player)
        return Response(serializer.data)
