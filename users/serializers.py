from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """
    Сериализатор для модели User.

    Сериализует/десериализует основные поля пользователя.
    Пароль обрабатывается отдельно (только для записи, не отображается при чтении).
    """

    class Meta:
        model = User
        fields = ["id", "email", "phone", "tg_chat_id"]
        extra_kwargs = {"password": {"write_only": True}}
