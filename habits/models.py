from django.db import models

from habits.validators import (validate_enjoyable_habit,
                               validate_periodicity_object,
                               validate_related_habit,
                               validate_reward_and_related,
                               validate_time_limit)
from users.models import User


class Periodicity(models.Model):
    """
    Модель периодичности выполнения привычки.

    Attributes:
        value (PositiveIntegerField): Числовое значение периодичности
        unit (CharField): Единица измерения периодичности (минуты/часы/дни/недели)
    """

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
        """
        Возвращает строковое представление периодичности с правильным склонением.

        Returns:
            str: Описание периодичности с правильным склонением (например, "Каждые 2 дня")
        """
        if self.value == 1:
            if self.unit == "days":
                return "Ежедневно"
            elif self.unit == "week":
                return "Еженедельно"
            elif self.unit == "hours":
                return "Ежечасно"
            elif self.unit == "minutes":
                return "Ежеминутно"

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

    def clean(self):
        """Валидация модели"""
        validate_periodicity_object(self)

    def save(self, *args, **kwargs):
        """Сохранение с валидацией"""
        self.full_clean()
        super().save(*args, **kwargs)


class Habit(models.Model):
    """
    Модель привычки пользователя.

    Attributes:
        creator (ForeignKey): Создатель привычки (связь с User)
        place (CharField): Место выполнения привычки
        habit_time (TimeField): Время выполнения привычки
        action (CharField): Действие, представляющее привычку
        enjoyable_habit (BooleanField): Признак приятной привычки
        related_habit (ForeignKey): Связанная привычка (связь с Habit)
        periodicity (ForeignKey): Периодичность выполнения (связь с Periodicity)
        reward (CharField): Вознаграждение за выполнение
        time_to_complete (PositiveIntegerField): Время на выполнение (в секундах)
        publicity (BooleanField): Признак публичности привычки
    """

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
        verbose_name="Время на выполнение (в секундах)",
    )
    publicity = models.BooleanField(default=False, verbose_name="Признак публичности")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]

    def __str__(self):
        """Строковое представление привычки."""
        return f"Я буду {self.action} в {self.habit_time} в {self.place}"

    def clean(self):
        """
        Валидация модели перед сохранением.

        Проверяет:
        - Взаимоисключение вознаграждения и связанной привычки
        - Ограничение времени выполнения
        - Корректность связанной привычки
        - Корректность приятной привычки
        - Валидность периодичности
        """
        validate_reward_and_related(self.reward, self.related_habit)
        validate_time_limit(self.time_to_complete)
        if self.related_habit:
            validate_related_habit(self.related_habit)
        validate_enjoyable_habit(self.enjoyable_habit, self.reward, self.related_habit)

    def save(self, *args, **kwargs):
        """
        Переопределение метода сохранения с предварительной валидацией.
        """
        self.full_clean()
        super().save(*args, **kwargs)
