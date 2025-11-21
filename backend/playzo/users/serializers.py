from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    url = HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk')

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'is_superuser', 'password', 'password2', 'url']

    def validate(self, data):
        if 'password' in data and 'password2' in data:
            if data['password'] != data['password2']:
                raise serializers.ValidationError(
                    {'password': 'passwords do not match', 'password2': 'passwords do not match'})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2')
        is_superuser = validated_data.pop('is_superuser', False)

        user = super().create(validated_data)

        if is_superuser:
            user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        user = super().update(instance, validated_data)
        if password and password2:
            user.set_password(password)
        user.save()
        return user
