from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from habits.services import send_telegram_message  # Импорт сервисной функции


@shared_task
def check_habits_and_send_reminders():
    """Асинхронная задача для проверки и отправки напоминаний"""
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        habit_time__hour=current_time.hour, habit_time__minute=current_time.minute
    )

    for habit in habits:
        if habit.creator.tg_chat_id:
            message = (
                f"Напоминание о привычке:\n"
                f"Я должен {habit.action} в {habit.habit_time}. Место выполнения: {habit.place}\n"
                f"Время на выполнение: {habit.time_to_complete} секунд"
            )
            send_telegram_message(habit.creator.tg_chat_id, message)
