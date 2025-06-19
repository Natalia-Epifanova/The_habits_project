from rest_framework import serializers

from habits.models import Habit, Periodicity
from habits.validators import (
    validate_enjoyable_habit,
    validate_periodicity,
    validate_related_habit,
    validate_reward_and_related,
    validate_time_limit,
)


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit.

    Attributes:
        creator (HiddenField): Автоматически устанавливает текущего пользователя как создателя
        periodicity (CharField): Строковое представление периодичности (только для чтения)
    """

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    periodicity = serializers.CharField(source="periodicity.__str__", read_only=True)

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
        related_habit_id = data.get("related_habit")
        enjoyable = data.get("enjoyable_habit")
        time_to_complete = data.get("time_to_complete", 0)
        periodicity_id = data.get("periodicity")

        related_habit = None
        if related_habit_id:
            related_habit = Habit.objects.get(pk=related_habit_id)

        periodicity = None
        if periodicity_id:
            periodicity = Periodicity.objects.get(pk=periodicity_id)

        validate_reward_and_related(reward, related_habit)
        validate_time_limit(time_to_complete)
        validate_related_habit(related_habit)
        validate_enjoyable_habit(enjoyable, reward, related_habit)
        validate_periodicity(periodicity)

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

    @staticmethod
    def get_display_name(obj):
        """
        Возвращает строковое представление периодичности.
        """
        return str(obj)
