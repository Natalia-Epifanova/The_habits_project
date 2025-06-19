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
        ("minutes", "минута/минуты/минут"),
        ("hours", "час/часа/часов"),
        ("days", "день/дня/дней"),
        ("week", "неделя/недели/недель"),
    ]

    value = models.PositiveIntegerField(verbose_name="Значение периодичности")
    unit = models.CharField(
        max_length=10, choices=PERIOD_CHOICES, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Периодичность"
        verbose_name_plural = "Периодичности"

    def __str__(self):
        if self.value == 1:
            if self.unit == "days":
                return "Ежедневно"
            elif self.unit == "week":
                return "Еженедельно"
            elif self.unit == "hours":
                return "Ежечасно"
            elif self.unit == "minutes":
                return "Ежеминутно"
            return f"Каждую {self.get_unit_display().split('/')[0]}"

        unit_parts = self.get_unit_display().split("/")
        if self.value % 10 == 1 and self.value % 100 != 11:
            unit = unit_parts[0]
        elif 2 <= self.value % 10 <= 4 and (
            self.value % 100 < 10 or self.value % 100 >= 20
        ):
            unit = unit_parts[1]
        else:
            unit = unit_parts[2]

        return f"Каждые {self.value} {unit}"


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
