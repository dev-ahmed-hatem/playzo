from rest_framework import serializers
from .models import Player
from users.serializers import UserSerializer
from users.models import User
from django.db import transaction


class PlayerReadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    # Add these fields to show score statistics
    win_rate = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            "id",
            "user",
            "name",
            "birthdate",
            "gender",
            "phone",
            "photo",
            "total_score",
            "high_score",
            "games_played",
            "games_won",
            "average_score",
            "last_game_score",
            "last_game_date",
            "win_rate",
            "rank",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "total_score",
            "high_score",
            "games_played",
            "games_won",
            "average_score",
            "last_game_score",
            "last_game_date",
            "created_at",
            "updated_at",
        ]

    def get_win_rate(self, obj):
        """Calculate win rate percentage"""
        if obj.games_played > 0:
            return round((obj.games_won / obj.games_played) * 100, 2)
        return 0.0

    def get_rank(self, obj):
        """Calculate player rank (you can implement your own ranking logic)"""
        # This is a simple implementation - you might want to query against all players
        if obj.total_score > 1000:
            return "Expert"
        elif obj.total_score > 500:
            return "Advanced"
        elif obj.total_score > 100:
            return "Intermediate"
        else:
            return "Beginner"


class PlayerWriteSerializer(serializers.ModelSerializer):
    # Nested fields for creating User
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Player
        fields = [
            "username",
            "password",
            "name",
            "birthdate",
            "gender",
            "phone",
            "photo",
            "email",
            "address",
            # Note: Score fields are not included here as they should be updated via actions
        ]
        read_only_fields = [
            "total_score",
            "high_score",
            "games_played",
            "games_won",
            "average_score",
            "last_game_score",
            "last_game_date",
        ]

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            raise serializers.ValidationError("Username already exists")
        except User.DoesNotExist:
            return value

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        validated_data["user"] = user
        player = super().create(validated_data)
        return player

    def update(self, instance, validated_data):
        # Update Player fields
        instance.name = validated_data.get("name", instance.name)
        instance.birthdate = validated_data.get("birthdate", instance.birthdate)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.photo = validated_data.get("photo", instance.photo)
        instance.email = validated_data.get("email", instance.email)
        instance.address = validated_data.get("address", instance.address)
        instance.save()

        # Update User password if provided
        password = validated_data.get("password", None)
        if password:
            instance.user.set_password(password)
            instance.user.save()

        return instance
