from django.core.exceptions import ValidationError
from rest_framework import serializers

from habits.constans import ERROR_MESSAGES


def validate_reward_and_related(reward, related_habit):
    """
    Проверяет, что указано только одно: либо вознаграждение, либо связанная привычка.

    Args:
        reward (str): Вознаграждение за выполнение
        related_habit (Habit): Связанная привычка

    Raises:
        ValidationError: Если указаны и вознаграждение, и связанная привычка
    """
    if reward and related_habit:
        raise serializers.ValidationError(ERROR_MESSAGES[0])


def validate_time_limit(time_to_complete):
    """
    Проверяет, что время выполнения не превышает 120 секунд.

    Args:
        time_to_complete (int): Время выполнения в секундах

    Raises:
        ValidationError: Если время превышает лимит
    """
    if time_to_complete > 120:
        raise serializers.ValidationError(ERROR_MESSAGES[1])


def validate_related_habit(related_habit):
    """
    Проверяет, что связанная привычка является приятной.

    Args:
        related_habit (Habit): Связанная привычка

    Raises:
        ValidationError: Если связанная привычка не является приятной
    """
    if related_habit and not related_habit.enjoyable_habit:
        raise ValidationError(ERROR_MESSAGES[2])


def validate_enjoyable_habit(enjoyable, reward, related_habit):
    """
    Проверяет, что у приятной привычки нет вознаграждения или связанной привычки.

    Args:
        enjoyable (bool): Является ли привычка приятной
        reward (str): Вознаграждение
        related_habit (Habit): Связанная привычка

    Raises:
        ValidationError: Если у приятной привычки указаны вознаграждение или связанная привычка
    """
    if enjoyable and (reward or related_habit):
        raise serializers.ValidationError(ERROR_MESSAGES[3])


def validate_periodicity_object(periodicity):
    """
    Проверяет корректность объекта Periodicity.

    Args:
        periodicity (Periodicity): Объект периодичности

    Raises:
        ValidationError: Если значение value превышает допустимый максимум для unit
            - для "days" больше 7
            - для "week" больше 1
    """
    if periodicity.unit == "days" and periodicity.value > 7:
        raise ValidationError(ERROR_MESSAGES[4])
    elif periodicity.unit == "week" and periodicity.value > 1:
        raise ValidationError(ERROR_MESSAGES[5])


def validate_periodicity_data(data):
    """
    Проверяет корректность данных периодичности из сериализатора.

    Args:
        data (dict): Словарь с ключами 'value' и 'unit'

    Raises:
        ValidationError: Если значение value превышает допустимый максимум для unit
            - для "days" больше 7
            - для "week" больше 1
    """
    unit = data.get("unit")
    value = data.get("value")

    if unit == "days" and value > 7:
        raise serializers.ValidationError(ERROR_MESSAGES[4])
    elif unit == "week" and value > 1:
        raise serializers.ValidationError(ERROR_MESSAGES[5])
