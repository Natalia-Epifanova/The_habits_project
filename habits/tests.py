from unittest.mock import Mock

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from habits.constans import ERROR_MESSAGES
from habits.models import Habit, Periodicity
from habits.validators import validate_periodicity_object
from habits.views import (
    HabitDeleteApiView,
    HabitListApiView,
    HabitRetrieveApiView,
    HabitUpdateApiView,
)
from users.models import User


class HabitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="testuser@mail.com")

        self.habit = Habit.objects.create(
            creator=self.user,
            action="Тестовое действие",
            place="Тестовое место",
            habit_time="08:00:00",
            reward="Тестовое вознаграждение",
            time_to_complete=60,
        )
        self.client.force_authenticate(user=self.user)

    def test_habit_retrieve(self):
        """Тест просмотра своей привычки обычным пользователем."""
        url = reverse("habits:habit_detail", args=(self.habit.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("action"), self.habit.action)
        self.assertEqual(data.get("place"), self.habit.place)
        self.assertEqual(
            data.get("habit_time"), self.habit.habit_time.strftime("%H:%M:%S")
        )
        self.assertEqual(data.get("reward"), self.habit.reward)
        self.assertEqual(data.get("time_to_complete"), self.habit.time_to_complete)
        self.assertEqual(data.get("periodicity_display"), "Ежедневно")

    def test_habit_create(self):
        """Тест создания своей привычки обычным пользователем."""
        url = reverse("habits:habit_create")
        data = {
            "action": "Тестовое действие 2",
            "place": "Тестовое место 2",
            "habit_time": "09:00:00",
            "reward": "Тестовое вознаграждение 2",
            "time_to_complete": 30,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.all().count(), 2)

    def test_habit_update(self):
        """Тест обновления своей привычки обычным пользователем."""
        url = reverse("habits:habit_update", args=(self.habit.pk,))
        data = {"action": "Тестовое действие переименованное"}
        response = self.client.patch(url, data)
        data_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data_response.get("action"), "Тестовое действие переименованное"
        )

    def test_habit_delete(self):
        """Тест удаления своей привычки обычным пользователем."""
        url = reverse("habits:habit_destroy", args=(self.habit.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.all().count(), 0)

    def test_habits_list(self):
        """Тест просмотра списка своих привычек обычным пользователем"""
        url = reverse("habits:habits_list")
        response = self.client.get(url)
        result = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.habit.pk,
                    "periodicity": 1,
                    "periodicity_display": "Ежедневно",
                    "place": self.habit.place,
                    "habit_time": self.habit.habit_time.strftime("%H:%M:%S"),
                    "action": self.habit.action,
                    "enjoyable_habit": False,
                    "reward": self.habit.reward,
                    "time_to_complete": self.habit.time_to_complete,
                    "publicity": False,
                    "related_habit": None,
                },
            ],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), result)

    def test_validate_time_limit(self):
        """Тест валидации ограничения времени выполнения привычки."""
        url = reverse("habits:habit_create")
        data = {
            "action": "Привычка с неправильным временем",
            "place": "Тестовое место",
            "habit_time": "10:00:00",
            "reward": "Тестовое вознаграждение",
            "time_to_complete": -5,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("time_to_complete", response.json())
        data = {
            "action": "Привычка с неправильным временем",
            "place": "Тестовое место",
            "habit_time": "10:00:00",
            "reward": "Тестовое вознаграждение",
            "time_to_complete": 140,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(ERROR_MESSAGES[1], response.json()["non_field_errors"])

    def test_validate_reward_and_related(self):
        """Тест валидации награды и связанной привычки при создании."""
        related_habit = Habit.objects.create(
            creator=self.user,
            action="Связанная привычка",
            place="Тестовое место",
            habit_time="07:00:00",
            time_to_complete=30,
            enjoyable_habit=True,
        )
        url = reverse("habits:habit_create")
        data = {
            "action": "Тестовое действие",
            "place": "Тестовое место",
            "habit_time": "09:00:00",
            "related_habit": related_habit.pk,
            "reward": "Тестовое вознаграждение",
            "time_to_complete": 30,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertIn(ERROR_MESSAGES[0], response.json()["non_field_errors"])

    def test_validate_related_habit(self):
        """Тест валидации связанной привычки в модели и через API."""
        related_habit = Habit.objects.create(
            creator=self.user,
            action="Связанная привычка",
            place="Тестовое место",
            habit_time="07:00:00",
            time_to_complete=30,
            enjoyable_habit=False,
        )
        habit = Habit(
            creator=self.user,
            action="Тестовое действие",
            place="Тестовое место",
            habit_time="09:00:00",
            time_to_complete=30,
            related_habit=related_habit,
        )
        with self.assertRaises(ValidationError) as cm:
            habit.full_clean()
        self.assertIn(ERROR_MESSAGES[2], str(cm.exception))

        url = reverse("habits:habit_create")
        data = {
            "action": "Тестовое действие",
            "place": "Тестовое место",
            "habit_time": "09:00:00",
            "related_habit": related_habit.pk,
            "time_to_complete": 30,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertIn(ERROR_MESSAGES[2], response.json()["non_field_errors"])

    def test_validate_enjoyable_habit(self):
        """Тест валидации признака приятной привычки при создании."""
        url = reverse("habits:habit_create")
        data = {
            "action": "Тестовое действие",
            "place": "Тестовое место",
            "habit_time": "09:00:00",
            "reward": "Тестовое вознаграждение",
            "time_to_complete": 30,
            "enjoyable_habit": True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertIn(ERROR_MESSAGES[3], response.json()["non_field_errors"])

    def test_get_queryset_swagger_fake_view_update(self):
        """Тест получения queryset для swagger fake view обновления."""
        view = HabitUpdateApiView()
        view.swagger_fake_view = True
        view.request = Mock()
        view.request.user = self.user
        qs = view.get_queryset()
        self.assertQuerySetEqual(qs, Habit.objects.none())

    def test_get_queryset_swagger_fake_view_retrieve(self):
        """Тест получения queryset для swagger fake view просмотра."""
        view = HabitRetrieveApiView()
        view.swagger_fake_view = True
        view.request = Mock()
        view.request.user = self.user
        qs = view.get_queryset()
        self.assertQuerySetEqual(qs, Habit.objects.none())

    def test_get_queryset_swagger_fake_view_delete(self):
        """Тест получения queryset для swagger fake view удаления."""
        view = HabitDeleteApiView()
        view.swagger_fake_view = True
        view.request = Mock()
        view.request.user = self.user
        qs = view.get_queryset()
        self.assertQuerySetEqual(qs, Habit.objects.none())

    def test_get_queryset_swagger_fake_view_list(self):
        """Тест получения queryset для swagger fake view списка."""
        view = HabitListApiView()
        view.swagger_fake_view = True
        view.request = Mock()
        view.request.user = self.user
        qs = view.get_queryset()
        self.assertQuerySetEqual(qs, Habit.objects.none())

    def test_habit_str(self):
        """Тест метода __str__ модели Habit."""
        expected_str = (
            f"Я буду {self.habit.action} в {self.habit.habit_time} в {self.habit.place}"
        )
        self.assertEqual(str(self.habit), expected_str)


class PeriodicityTestCase(APITestCase):
    def setUp(self):
        self.periodicity = Periodicity.objects.create(value=1, unit="hours")
        self.user = User.objects.create(email="testuser@mail.com")
        self.client.force_authenticate(user=self.user)

    def test_periodicity_retrieve(self):
        """Тест просмотра созданной периодичности."""
        url = reverse("habits:periodicity-detail", args=(self.periodicity.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("value"), self.periodicity.value)
        self.assertEqual(data.get("unit"), self.periodicity.unit)
        self.assertEqual(str(self.periodicity), "Ежечасно")

    def test_periodicity_create(self):
        """Тест создания новой периодичности."""
        url = reverse("habits:periodicity-list")
        data = {"value": 3, "unit": "days"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Periodicity.objects.all().count(), 3)

    def test_periodicity_update(self):
        """Тест обновления периодичности."""
        url = reverse("habits:periodicity-detail", args=(self.periodicity.pk,))
        data = {"value": 5}
        response = self.client.patch(url, data)
        data_response = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data_response.get("value"), 5)

    def test_periodicity_delete(self):
        """Тест удаления периодичности."""
        url = reverse("habits:periodicity-detail", args=(self.periodicity.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Periodicity.objects.all().count(), 1)

    def test_periodicity_list(self):
        """Тест просмотра списка периодичностей."""
        url = reverse("habits:periodicity-list")
        response = self.client.get(url)
        result = [
            {"id": 1, "display_name": "Ежедневно", "value": 1, "unit": "days"},
            {"id": 5, "display_name": "Ежечасно", "value": 1, "unit": "hours"},
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), result)

    def test_validate_periodicity(self):
        """Тест валидации периодичности с неверными значениями."""
        url = reverse("habits:periodicity-list")
        data = {"value": 3, "unit": "week"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertIn(ERROR_MESSAGES[5], response.json()["non_field_errors"])
        data = {"value": 8, "unit": "days"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.json())
        self.assertIn(ERROR_MESSAGES[4], response.json()["non_field_errors"])

    def test_periodicity_object_validation_invalid_days(self):
        """Тест валидации объекта Periodicity с недопустимым количеством дней (>7)."""
        periodicity = Periodicity(value=8, unit="days")
        with self.assertRaises(ValidationError) as context:
            validate_periodicity_object(periodicity)

        self.assertEqual(context.exception.messages[0], ERROR_MESSAGES[4])

    def test_periodicity_object_validation_invalid_weeks(self):
        """Тест валидации объекта Periodicity с недопустимым количеством недель (>1)."""
        periodicity = Periodicity(value=2, unit="week")
        with self.assertRaises(ValidationError) as context:
            validate_periodicity_object(periodicity)

        self.assertEqual(context.exception.messages[0], ERROR_MESSAGES[5])

    def test_str_method(self):
        """Тест метода __str__ модели Periodicity с разными значениями."""
        test_cases = [
            (1, "days", "Ежедневно"),
            (1, "week", "Еженедельно"),
            (1, "hours", "Ежечасно"),
            (1, "minutes", "Ежеминутно"),
            (21, "hours", "Каждые 21 час"),
            (2, "days", "Каждые 2 дня"),
            (5, "days", "Каждые 5 дней"),
            (11, "days", "Каждые 11 дней"),
            (3, "hours", "Каждые 3 часа"),
            (4, "minutes", "Каждые 4 минуты"),
            (22, "minutes", "Каждые 22 минуты"),
            (14, "week", "Каждые 14 недель"),
            (1, "week", "Еженедельно"),
        ]
        for value, unit, expected_str in test_cases:
            periodicity = Periodicity(value=value, unit=unit)
            self.assertEqual(str(periodicity), expected_str)
