from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from habits.constans import ERROR_MESSAGES
from habits.validtors import (validate_enjoyable_habit, validate_periodicity,
                              validate_related_habit,
                              validate_reward_and_related, validate_time_limit)
from users.models import User


class Periodicity(models.Model):
    PERIOD_CHOICES = [
        ("minutes", "Минуты"),
        ("hours", "Часы"),
        ("days", "Дни"),
        ("weeks", "Недели"),
    ]

    value = models.PositiveIntegerField(verbose_name="Значение периодичности")
    unit = models.CharField(
        max_length=10, choices=PERIOD_CHOICES, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Периодичность"
        verbose_name_plural = "Периодичности"

    def __str__(self):
        return f"Каждые {self.value} {self.unit}"


class Habit(models.Model):

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
    periodicity = models.ForeignKey(
        "Periodicity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=1,
        verbose_name="Периодичность выполнения",
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

    def clean(self):
        validate_reward_and_related(self.reward, self.related_habit)
        validate_time_limit(self.time_to_complete)
        if self.related_habit:
            validate_related_habit(self.related_habit)
        validate_enjoyable_habit(self.enjoyable_habit, self.reward, self.related_habit)
        if self.periodicity:
            validate_periodicity(self.periodicity)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
