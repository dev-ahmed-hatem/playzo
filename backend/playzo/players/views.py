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
        if self.action in ["create"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()

        ordering = self.request.query_params.get('ordering', None)
        if ordering in ['total_score', 'high_score', 'average_score', 'games_won']:
            queryset = queryset.order_by(f'-{ordering}')
        elif ordering == 'name':
            queryset = queryset.order_by('name')

        # Filter by minimum score if provided
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            try:
                queryset = queryset.filter(total_score__gte=int(min_score))
            except ValueError:
                pass

        return queryset

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        try:
            player = request.user.player
            serializer = self.get_serializer(player)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def add_score(self, request, pk=None):
        player = self.get_object()

        # Check if user owns this player profile or is admin
        if not (request.user == player.user or request.user.is_staff):
            return Response(
                {"error": "You can only update your own score"},
                status=status.HTTP_403_FORBIDDEN
            )

        score = request.data.get('score')
        if score is None:
            return Response(
                {"error": "Score is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            score = int(score)
            if score < 0:
                return Response(
                    {"error": "Score must be positive"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "Score must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update player's score statistics
        player.update_score_stats(score)

        # Check if player won (you can define your own win condition)
        won = request.data.get('won', False)
        if won:
            player.increment_games_won()

        serializer = self.get_serializer(player)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def increment_wins(self, request, pk=None):
        """Increment win count"""
        player = self.get_object()

        # Check if user owns this player profile or is admin
        if not (request.user == player.user or request.user.is_staff):
            return Response(
                {"error": "You can only update your own stats"},
                status=status.HTTP_403_FORBIDDEN
            )

        player.increment_games_won()
        serializer = self.get_serializer(player)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def leaderboard(self, request):
        """Get top players by different criteria"""
        criteria = request.query_params.get('by', 'total_score')
        limit = int(request.query_params.get('limit', 10))

        valid_criteria = ['total_score', 'high_score', 'average_score', 'games_won']
        if criteria not in valid_criteria:
            criteria = 'total_score'

        top_players = Player.objects.all().order_by(f'-{criteria}')[:limit]
        serializer = self.get_serializer(top_players, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def rankings(self, request):
        """Get player rankings with position"""
        criteria = request.query_params.get('by', 'total_score')
        valid_criteria = ['total_score', 'high_score', 'average_score', 'games_won']

        if criteria not in valid_criteria:
            criteria = 'total_score'

        players = Player.objects.all().order_by(f'-{criteria}', "name")

        # Create rankings with position
        rankings = []
        for index, player in enumerate(players, start=1):
            player_data = PlayerReadSerializer(player, context={"request": request}).data
            player_data['rank_position'] = index
            rankings.append(player_data)

        return Response(rankings)

    def _get_player_stats(self, player):
        """Helper method to get player statistics shared between stats and my_stats"""
        return {
            'player': player.name,
            'player_id': player.id,
            'total_score': player.total_score,
            'high_score': player.high_score,
            'games_played': player.games_played,
            'games_won': player.games_won,
            'games_lost': player.games_played - player.games_won,
            'average_score': player.average_score,
            'win_rate': round((player.games_won / player.games_played * 100), 2) if player.games_played > 0 else 0,
            'last_game_score': player.last_game_score,
            'last_game_date': player.last_game_date,
            'score_per_game': player.total_score / player.games_played if player.games_played > 0 else 0,
        }

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request, pk=None):
        """Get detailed statistics for a player"""
        player = self.get_object()
        stats = self._get_player_stats(player)
        return Response(stats)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_stats(self, request):
        """Get current user's statistics"""
        try:
            player = request.user.player
            stats = self._get_player_stats(player)
            return Response(stats)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
