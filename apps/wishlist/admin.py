from django.contrib import admin
from .models import WishlistItem

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "product", "created_at")
    search_fields = ("user__email", "product__name")
    list_filter = ("user", "product", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "product")