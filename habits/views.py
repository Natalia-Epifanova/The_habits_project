from django.shortcuts import render
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.viewsets import ModelViewSet

from habits.models import Habit, Periodicity
from habits.paginations import CustomPagination
from habits.serializers import HabitSerializer, PeriodicitySerializer


class HabitCreateApiView(CreateAPIView):
    """API для создания привычек."""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer


class HabitUpdateApiView(UpdateAPIView):
    """API для обновления привычек."""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(creator=self.request.user)


class HabitRetrieveApiView(RetrieveAPIView):
    """API для просмотра привычки."""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(creator=self.request.user)


class HabitDeleteApiView(DestroyAPIView):
    """API для удаления привычки"""

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(creator=self.request.user)


class HabitListApiView(ListAPIView):
    """API для просмотра списка привычек."""

    serializer_class = HabitSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Habit.objects.filter(creator=self.request.user)


class HabitPublicListApiView(ListAPIView):
    """API для просмотра списка публичных привычек."""

    queryset = Habit.objects.filter(publicity=True)
    serializer_class = HabitSerializer
    pagination_class = CustomPagination


class PeriodicityViewSet(ModelViewSet):
    """ViewSet для работы с периодичностью"""

    queryset = Periodicity.objects.all()
    serializer_class = PeriodicitySerializer
