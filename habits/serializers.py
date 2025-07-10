from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from habits.models import Habit, Periodicity
from habits.validators import (
    validate_enjoyable_habit,
    validate_periodicity_data,
    validate_related_habit,
    validate_reward_and_related,
    validate_time_limit,
)


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit.

    Attributes:
        creator (HiddenField): Автоматически устанавливает текущего пользователя как создателя
        periodicity_display (CharField): Строковое представление периодичности (только для чтения)
    """

    related_habit = serializers.PrimaryKeyRelatedField(
        queryset=Habit.objects.all(), allow_null=True, required=False
    )
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    periodicity = serializers.PrimaryKeyRelatedField(
        queryset=Periodicity.objects.all(), allow_null=True, required=False
    )
    periodicity_display = serializers.CharField(
        source="periodicity.__str__", read_only=True
    )

    class Meta:
        model = Habit
        fields = "__all__"

    def validate(self, data):
        """
        Валидация данных привычки перед сохранением.

        Args:
            data (dict): Данные для валидации

        Returns:
            dict: Валидные данные

        Raises:
            ValidationError: Если данные не проходят валидацию
        """
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        enjoyable = data.get("enjoyable_habit")
        time_to_complete = data.get("time_to_complete", 0)

        validate_reward_and_related(reward, related_habit)
        validate_time_limit(time_to_complete)
        try:
            validate_related_habit(related_habit)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        validate_enjoyable_habit(enjoyable, reward, related_habit)

        return data


class PeriodicitySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Periodicity.

    Attributes:
        display_name (SerializerMethodField): Человекочитаемое представление периодичности
    """

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Periodicity
        fields = "__all__"

    def validate(self, data):
        """Валидация данных в сериализаторе"""
        validate_periodicity_data(data)
        return data

    @staticmethod
    def get_display_name(obj):
        """
        Возвращает строковое представление периодичности.
        """
        return str(obj)
