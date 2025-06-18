from rest_framework import serializers

from habits.constans import ERROR_MESSAGES
from habits.models import Habit, Periodicity


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"

    def validate(self, data):
        if data.get("reward") and data.get("related_habit"):
            raise serializers.ValidationError(ERROR_MESSAGES[0])

        if data.get("time_to_complete", 0) > 120:
            raise serializers.ValidationError(ERROR_MESSAGES[1])

        related_habit_id = data.get("related_habit")
        if related_habit_id:
            related_habit = Habit.objects.get(pk=related_habit_id)
            if not related_habit.enjoyable_habit:
                raise serializers.ValidationError(ERROR_MESSAGES[2])

        if data.get("enjoyable_habit") and (
            data.get("reward") or data.get("related_habit")
        ):
            raise serializers.ValidationError(ERROR_MESSAGES[3])

        periodicity_id = data.get("periodicity")
        if periodicity_id:
            periodicity = Periodicity.objects.get(pk=periodicity_id)
            if periodicity.unit == "days" and periodicity.value > 7:
                raise serializers.ValidationError(ERROR_MESSAGES[4])
            elif periodicity.unit == "weeks" and periodicity.value > 1:
                raise serializers.ValidationError(ERROR_MESSAGES[5])

        return data
