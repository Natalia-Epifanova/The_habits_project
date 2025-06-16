from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models

from users.models import User


class Periodicity(models.Model):
    PERIOD_CHOICES = [
        ('minutes', 'Минуты'),
        ('hours', 'Часы'),
        ('days', 'Дни'),
        ('weeks', 'Недели'),
    ]

    value = models.PositiveIntegerField(verbose_name="Значение периодичности")
    unit = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        verbose_name="Единица измерения"
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
        'Periodicity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Периодичность выполнения"
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
        if self.reward and self.related_habit:
            raise ValidationError("Вознаграждение и связанная привычка не могут быть указаны одновременно")
        if self.time_to_complete > 120:
            raise ValidationError("Время выполнения должно быть не больше 120 секунд.")
        if self.related_habit and not self.related_habit.enjoyable_habit:
            raise ValidationError("В связанные привычки могут попадать только привычки с признаком приятной привычки.")
        if self.enjoyable_habit and (self.reward or self.related_habit):
            raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки")
        if self.periodicity:
            if self.periodicity.unit == 'days' and self.periodicity.value > 7:
                raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")
            elif self.periodicity.unit == 'weeks' and self.periodicity.value > 1:
                raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в неделю")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)