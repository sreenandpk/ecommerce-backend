from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Ingredient, Nutrition, Allergen, City, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "image_preview", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Image"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "pincode")
    search_fields = ("name", "pincode")
    ordering = ("name",)


class NutritionInline(admin.StackedInline):
    model = Nutrition
    can_delete = False
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "name",
        "slug",
        "price",
        "currency",
        "stock",
        "is_active",
        "created_at",
        "category",
    )
    list_filter = ("category", "currency", "is_active", "created_at")
    search_fields = ("name", "slug", "description", "story")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("ingredients", "allergens", "available_cities")
    inlines = [NutritionInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit:cover;border-radius:5px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Image"
