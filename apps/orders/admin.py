# apps/orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


# =========================
# ORDER ITEM INLINE
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    readonly_fields = (
        "product",
        "quantity",
        "price",
        "subtotal",
    )

    def has_add_permission(self, request, obj=None):
        return False


# =========================
# ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "total_amount",
        "status",
        "is_paid",
        "items_count",
        "created_at",
    )

    list_filter = (
        "status",
        "is_paid",
        "created_at",
    )

    search_fields = (
        "id",
        "full_name",
        "phone",
        "user__email",
    )

    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
        "updated_at",
    )

    list_editable = ("status",)

    inlines = [OrderItemInline]

    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    def items_count(self, obj):
        return obj.items.count()

    items_count.short_description = "Items"


# =========================
# ORDER ITEM ADMIN
# =========================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "quantity",
        "price",
        "subtotal",
    )

    readonly_fields = (
        "order",
        "product",
        "quantity",
        "price",
        "subtotal",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def status_colored(self, obj):
        color = {
            "pending": "orange",
            "paid": "green",
            "shipped": "blue",
            "delivered": "darkgreen",
            "cancelled": "red",
        }.get(obj.status, "black")

        return format_html(
            '<strong style="color:{};">{}</strong>',
            color,
            obj.status.upper()
        )

    status_colored.short_description = "Status"
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == "delivered":
            return self.readonly_fields + ("status",)
        return self.readonly_fields
