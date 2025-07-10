from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from users.models import User
from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """
    API endpoint для регистрации новых пользователей.
    Доступен без аутентификации (AllowAny).
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


class UserRetrieveAPIView(RetrieveAPIView):
    """
    API endpoint для просмотра профиля пользователя.
    Возвращает основные данные пользователя: email, телефон и telegram chat_id.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
