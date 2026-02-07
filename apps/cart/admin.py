from django.contrib import admin
from .models import CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user_email", "product", "quantity", "subtotal", "created_at")
    search_fields = ("user__email", "product__name")
    list_filter = ("user", "product", "created_at")
    ordering = ("-id",)
    readonly_fields = ("created_at",)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "User Email"

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Subtotal"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "product")