from django.contrib import admin
from django.contrib.admin import ModelAdmin

from habits.models import Habit, Periodicity


@admin.register(Periodicity)
class PeriodicityAdmin(ModelAdmin):
    list_filter = ("id", "value", "unit")


@admin.register(Habit)
class HabitAdmin(ModelAdmin):
    list_filter = (
        "creator",
        "place",
        "habit_time",
        "action",
        "enjoyable_habit",
        "related_habit",
        "periodicity",
        "reward",
        "time_to_complete",
        "publicity",
    )
