import requests

from config.settings import BOT_TOKEN, TELEGRAM_URL


def send_telegram_message(chat_id, message):
    """
    Отправляет сообщение в Telegram через API.

    Args:
        chat_id (str): ID чата в Telegram
        message (str): Текст сообщения

    Returns:
        dict: Ответ от Telegram API или None в случае ошибки
    """
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
