from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit, Periodicity
from habits.paginations import CustomPagination
from habits.serializers import HabitSerializer, PeriodicitySerializer


class HabitCreateApiView(CreateAPIView):
    """
    API endpoint для создания новых привычек.
    Поддерживает POST запросы с данными новой привычки.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer


class HabitUpdateApiView(UpdateAPIView):
    """
    API endpoint для обновления существующих привычек.
    Доступно только для привычек, созданных текущим пользователем.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя."""
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(creator=self.request.user)


class HabitRetrieveApiView(RetrieveAPIView):
    """
    API endpoint для просмотра деталей конкретной привычки.
    Доступно только для привычек, созданных текущим пользователем.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя."""
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(creator=self.request.user)


class HabitDeleteApiView(DestroyAPIView):
    """
    API endpoint для удаления привычек.
    Доступно только для привычек, созданных текущим пользователем.
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя."""
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(creator=self.request.user)


class HabitListApiView(ListAPIView):
    """
    API endpoint для просмотра списка привычек текущего пользователя.
    """

    serializer_class = HabitSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Возвращает только привычки текущего пользователя."""
        if getattr(self, "swagger_fake_view", False):
            return Habit.objects.none()
        return Habit.objects.filter(creator=self.request.user)


class HabitPublicListApiView(ListAPIView):
    """
    API endpoint для просмотра публичных привычек всех пользователей.
    """

    queryset = Habit.objects.filter(publicity=True)
    serializer_class = HabitSerializer
    pagination_class = CustomPagination


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description="Получение списка всех периодичностей."
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_description="Создание новой периодичности."
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_description="Просмотр детальной информации о периодичности."
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_description="Полное обновление периодичности."
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_description="Частичное обновление периодичности. "
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(operation_description="Удаление периодичности."),
)
class PeriodicityViewSet(ModelViewSet):
    """
    ViewSet для работы с периодичностями выполнения привычек.
    Поддерживает все стандартные операции CRUD.
    """

    queryset = Periodicity.objects.all()
    serializer_class = PeriodicitySerializer
