from django.core.exceptions import ValidationError
from rest_framework import serializers

from habits.constans import ERROR_MESSAGES


def validate_reward_and_related(reward, related_habit):
    """Проверка взаимного исключения вознаграждения и связанной привычки."""
    if reward and related_habit:
        raise serializers.ValidationError(ERROR_MESSAGES[0])


def validate_time_limit(time_to_complete):
    """Проверка времени выполнения."""
    if time_to_complete > 120:
        raise serializers.ValidationError(ERROR_MESSAGES[1])


def validate_related_habit(related_habit):
    """Проверяет, что связанная привычка является приятной."""
    if related_habit and not related_habit.enjoyable_habit:
        raise serializers.ValidationError(ERROR_MESSAGES[2])


def validate_enjoyable_habit(enjoyable, reward, related_habit):
    """Проверка приятной привычки."""
    if enjoyable and (reward or related_habit):
        raise serializers.ValidationError(ERROR_MESSAGES[3])


def validate_periodicity(periodicity):
    """Проверка периодичности."""
    if periodicity:
        if periodicity.unit == "days" and periodicity.value > 7:
            raise serializers.ValidationError(ERROR_MESSAGES[4])
        elif periodicity.unit == "weeks" and periodicity.value > 1:
            raise serializers.ValidationError(ERROR_MESSAGES[5])
