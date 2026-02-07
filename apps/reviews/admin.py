from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # REQUIRED for autocomplete_fields
    search_fields = (
        "user__username",
        "user__email",
        "product__name",
        "comment",
    )

    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "short_comment",
        "is_active",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_active",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "product",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_editable = ("is_active",)

    list_per_page = 25

    @admin.display(description="Comment")
    def short_comment(self, obj):
        if not obj.comment:
            return "-"
        return obj.comment[:40] + ("..." if len(obj.comment) > 40 else "")
