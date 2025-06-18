from django.urls import path

from habits.apps import HabitsConfig
from habits.views import (HabitCreateApiView, HabitDeleteApiView,
                          HabitListApiView, HabitPublicListApiView,
                          HabitRetrieveApiView, HabitUpdateApiView)

app_name = HabitsConfig.name

urlpatterns = [
    path("", HabitListApiView.as_view(), name="habits_list"),
    path("public/", HabitPublicListApiView.as_view(), name="habits_public_list"),
    path("create/", HabitCreateApiView.as_view(), name="habit_create"),
    path("<int:pk>/", HabitRetrieveApiView.as_view(), name="habit_detail"),
    path("<int:pk>/update/", HabitUpdateApiView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteApiView.as_view(), name="habit_destroy"),
]
