import requests

from config.settings import BOT_TOKEN, TELEGRAM_URL


def send_telegram_message(chat_id, message):
    """Синхронная отправка сообщения в Telegram"""
    params = {
        "text": message,
        "chat_id": chat_id,
    }
    try:
        response = requests.post(
            f"{TELEGRAM_URL}{BOT_TOKEN}/sendMessage", params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return None
