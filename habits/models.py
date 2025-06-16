from django.core.validators import MaxValueValidator
from django.db import models

from users.models import User


class Habit(models.Model):
    PERIODICITY_CHOICES = [
        ("daily", "Ежедневно"),
        ("weekly", "Еженедельно"),
    ]

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Создатель"
    )
    place = models.CharField(max_length=100, verbose_name="Место выполнения привычки")
    habit_time = models.TimeField(verbose_name="Время выполнения привычки")
    action = models.CharField(max_length=200, verbose_name="Действие")
    enjoyable_habit = models.BooleanField(
        default=False, verbose_name="Признак приятной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
    )
    periodicity = models.CharField(
        max_length=10,
        choices=PERIODICITY_CHOICES,
        default="daily",
        verbose_name="Периодичность выполнения привычки",
    )
    reward = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Вознаграждение"
    )
    time_to_complete = models.PositiveIntegerField(
        validators=[MaxValueValidator(120)],
        verbose_name="Время на выполнение (в секундах)",
    )
    publicity = models.BooleanField(default=False, verbose_name="Признак публичности")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self):
        return f"Я буду {self.action} в {self.habit_time} в {self.place}"
