from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя на основе AbstractUser.
    Использует email в качестве основного идентификатора вместо username.

    Attributes:
        email (EmailField): Уникальный email пользователя (используется для входа)
        phone (CharField): Номер телефона (необязательный)
        tg_chat_id (CharField): ID чата в Telegram для уведомлений (необязательный)
    """

    username = None

    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=35, blank=True, null=True, verbose_name="Телефон"
    )
    tg_chat_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Чат-id в телеграме"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Строковое представление пользователя (email)."""
        return self.email
