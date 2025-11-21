from rest_framework import serializers
from .models import Player
from users.serializers import UserSerializer
from users.models import User


class PlayerReadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "user",
            "birthdate",
            "gender",
            "phone",
            "photo",
            "created_at",
            "updated_at",
        ]


class PlayerWriteSerializer(serializers.ModelSerializer):
    # Nested fields for creating User
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Player
        fields = [
            "username",
            "password",
            "birthdate",
            "gender",
            "phone",
            "photo",
        ]

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")

        user = User.objects.create(username=username)
        user.set_password(password)  # hash the password
        user.save()

        # Create the Player linked to this user
        player = Player.objects.create(user=user, **validated_data)
        return player

    def update(self, instance, validated_data):
        # Update Player fields
        instance.birthdate = validated_data.get("birthdate", instance.birthdate)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.photo = validated_data.get("photo", instance.photo)
        instance.save()

        # Update User password if provided
        password = validated_data.get("password", None)
        if password:
            instance.user.set_password(password)
            instance.user.save()

        return instance
