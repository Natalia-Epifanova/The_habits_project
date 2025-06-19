from django.urls import path
from rest_framework.routers import DefaultRouter

from habits.apps import HabitsConfig
from habits.views import (
    HabitCreateApiView,
    HabitDeleteApiView,
    HabitListApiView,
    HabitPublicListApiView,
    HabitRetrieveApiView,
    HabitUpdateApiView,
    PeriodicityViewSet,
)

app_name = HabitsConfig.name
router = DefaultRouter()
router.register(r"periodicity", PeriodicityViewSet)

urlpatterns = [
    path("", HabitListApiView.as_view(), name="habits_list"),
    path("public/", HabitPublicListApiView.as_view(), name="habits_public_list"),
    path("create/", HabitCreateApiView.as_view(), name="habit_create"),
    path("<int:pk>/", HabitRetrieveApiView.as_view(), name="habit_detail"),
    path("<int:pk>/update/", HabitUpdateApiView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteApiView.as_view(), name="habit_destroy"),
] + router.urls
