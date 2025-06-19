from django.contrib import admin
from django.contrib.admin import ModelAdmin

from users.models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    """Административный интерфейс для модели User."""

    list_filter = ("id", "email", "tg_chat_id")
