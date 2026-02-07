from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "is_active",
        "is_staff",
    )
