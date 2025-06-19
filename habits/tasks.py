from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from habits.services import send_telegram_message  # Импорт сервисной функции


@shared_task
def check_habits_and_send_reminders():
    """
    Периодическая задача для проверки и отправки напоминаний о привычках.

    Проверяет привычки, которые должны быть выполнены в текущее время,
    и отправляет уведомления в Telegram.

    Логика:
    1. Получает текущее время (с учетом часового пояса)
    2. Находит привычки, запланированные на это время
    3. Для каждой привычки отправляет напоминание в Telegram
    """
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        habit_time__hour=current_time.hour + 3,
        habit_time__minute=current_time.minute,
        creator__isnull=False,
    )

    for habit in habits:
        if habit.creator.tg_chat_id:
            message = (
                f"Напоминание о привычке:\n"
                f"Я должен {habit.action} в {habit.habit_time}. Место выполнения: {habit.place}\n"
                f"Время на выполнение: {habit.time_to_complete} секунд"
            )
            send_telegram_message(habit.creator.tg_chat_id, message)
