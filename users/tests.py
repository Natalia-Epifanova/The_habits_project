from unittest import TestCase
from unittest.mock import Mock, patch

import requests
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config.settings import BOT_TOKEN
from habits.models import Habit
from users.models import User
from users.services import send_telegram_message
from users.tasks import check_habits_and_send_reminders


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@mail.com")
        self.user.set_password("testpassword")
        self.user.save()

    def test_user_create(self):
        """Тест создания нового пользователя."""
        url = reverse("users:register")
        data = {
            "email": "newuser@mail.com",
            "password": "new_password_123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@mail.com").exists())

        created_user = User.objects.get(email="newuser@mail.com")
        self.assertNotEqual(created_user.password, data["password"])
        self.assertTrue(created_user.check_password(data["password"]))
        self.assertTrue(created_user.is_active)

    def test_user_create_missing_fields(self):
        """Тест создания пользователя с неполными данными."""
        url = reverse("users:register")
        data = {
            "email": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())
        self.assertIn("password", response.json())

    def test_user_retrieve_unauthenticated(self):
        """Тест получения профиля без аутентификации."""
        url = reverse("users:profile", args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_retrieve_authenticated(self):
        """Тест получения профиля с аутентификацией."""
        self.client.force_authenticate(user=self.user)
        url = reverse("users:profile", args=(self.user.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get("email"), self.user.email)

    def test_user_str(self):
        """Тест строкового представления пользователя."""
        self.assertEqual(str(self.user), self.user.email)


class TelegramUtilsTestCase(APITestCase):
    @patch("users.services.requests.post")
    def test_send_telegram_message_success(self, mock_post):
        """Тест успешной отправки сообщения в Telegram."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}
        mock_post.return_value = mock_response

        chat_id = "123456"
        message = "Тестовое сообщение"

        result = send_telegram_message(chat_id, message)

        mock_post.assert_called_once()
        called_url = mock_post.call_args[0][0]
        called_params = mock_post.call_args[1]["params"]

        self.assertIn(BOT_TOKEN, called_url)
        self.assertEqual(called_params["chat_id"], chat_id)
        self.assertEqual(called_params["text"], message)

        self.assertEqual(result, {"ok": True, "result": {"message_id": 123}})

    @patch("users.services.requests.post")
    def test_send_telegram_message_http_error(self, mock_post):
        """Тест ошибки HTTP при отправке сообщения."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Error"
        )
        mock_post.return_value = mock_response

        chat_id = "123456"
        message = "Тестовое сообщение"

        result = send_telegram_message(chat_id, message)

        self.assertIsNone(result)

    @patch("users.services.requests.post")
    def test_send_telegram_message_request_exception(self, mock_post):
        """Тест исключения при отправке сообщения."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        chat_id = "123456"
        message = "Тестовое сообщение"

        result = send_telegram_message(chat_id, message)

        self.assertIsNone(result)


class HabitTasksTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@mail.com", tg_chat_id="123456")
        self.habit = Habit.objects.create(
            creator=self.user,
            action="Тестовое действие",
            place="Тестовое место",
            habit_time="12:00:00",
            time_to_complete=60,
        )

    @patch("users.tasks.timezone.now")
    @patch("users.tasks.send_telegram_message")
    def test_check_habits_and_send_reminders_success(self, mock_send, mock_now):
        """Тест успешной отправки напоминания о привычке."""
        mock_now.return_value = timezone.datetime(2025, 1, 1, 9, 0)

        check_habits_and_send_reminders()

        expected_message = (
            "Напоминание о привычке:\n"
            "Я должен Тестовое действие в 12:00:00. Место выполнения: Тестовое место\n"
            "Время на выполнение: 60 секунд"
        )
        mock_send.assert_called_once_with("123456", expected_message)

    @patch("users.tasks.timezone.now")
    @patch("users.tasks.send_telegram_message")
    def test_check_habits_no_matching_time(self, mock_send, mock_now):
        """Тест отсутствия привычек для текущего времени."""
        mock_now.return_value = timezone.datetime(2023, 1, 1, 10, 0)

        check_habits_and_send_reminders()

        mock_send.assert_not_called()

    @patch("users.tasks.timezone.now")
    @patch("users.tasks.send_telegram_message")
    def test_check_habits_no_tg_chat_id(self, mock_send, mock_now):
        """Тест отсутствия tg_chat_id у пользователя."""
        self.user.tg_chat_id = None
        self.user.save()
        mock_now.return_value = timezone.datetime(2023, 1, 1, 9, 0)

        check_habits_and_send_reminders()

        mock_send.assert_not_called()


class CreateSuperuserCommandTestCase(TestCase):
    def test_create_superuser_command_creates_user(self):
        """Тест создания суперпользователя через команду."""
        call_command("csu")

        user = User.objects.filter(email="admin@example.com").first()
        self.assertIsNotNone(user, "Суперпользователь не был создан командой")

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

        self.assertTrue(user.check_password("12345qwerty"))
