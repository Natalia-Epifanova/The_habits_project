from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """
    Сериализатор для модели User.

    Сериализует/десериализует основные поля пользователя.
    Пароль обрабатывается отдельно (только для записи, не отображается при чтении).
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "tg_chat_id", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
