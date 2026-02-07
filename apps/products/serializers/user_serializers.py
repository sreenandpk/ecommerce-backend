from rest_framework import serializers
from django.db import transaction
from ..models import (
    Product,
    Ingredient,
    Nutrition,
    Allergen,
    Category,
)
class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_upload = serializers.ImageField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "image",   
            "image_upload",  
        ]
    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    def create(self, validated_data):
        image = validated_data.pop("image_upload", None)
        category = Category.objects.create(**validated_data)
        if image:
            category.image = image
            category.save()
        return category
    def update(self, instance, validated_data):
        image = validated_data.pop("image_upload", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if image:
            if instance.image:
                instance.image.delete(save=False)
            instance.image = image
        instance.save()
        return instance
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ["id", "calories", "protein", "fat", "carbs", "sugar"]
class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = ["id", "name"]
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    nutrition = NutritionSerializer(read_only=True)
    allergens = AllergenSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source="category"
    )
    ingredient_ids = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True,
        write_only=True
    )
    nutrition_data = NutritionSerializer(write_only=True)
    allergen_ids = serializers.PrimaryKeyRelatedField(
        queryset=Allergen.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    slug = serializers.ReadOnlyField()
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "category_id",
            "price",
            "currency",
            "image",
            "ingredients",
            "ingredient_ids",
            "nutrition",
            "nutrition_data",
            "allergens",
            "allergen_ids",
            "story",
            "description",
            "stock",
            "is_active",
            "created_at",
            "updated_at",
            "average_rating", 
            "review_count",
        ]
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value
    def validate_image(self, image):
        if image.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image must be under 2MB")
        return image
    @transaction.atomic
    def create(self, validated_data):
        ingredient_ids = validated_data.pop("ingredient_ids")
        nutrition_data = validated_data.pop("nutrition_data")
        allergen_ids = validated_data.pop("allergen_ids", [])
        nutrition = Nutrition.objects.create(**nutrition_data)
        product = Product.objects.create(
            nutrition=nutrition,
            **validated_data
        )
        product.ingredients.set(ingredient_ids)
        if allergen_ids:
            product.allergens.set(allergen_ids)
        return product
    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient_ids = validated_data.pop("ingredient_ids", None)
        nutrition_data = validated_data.pop("nutrition_data", None)
        allergen_ids = validated_data.pop("allergen_ids", None)
        if "image" in validated_data and instance.image:
            instance.image.delete(save=False)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if nutrition_data:
            for attr, value in nutrition_data.items():
                setattr(instance.nutrition, attr, value)
            instance.nutrition.save()
        if ingredient_ids is not None:
            instance.ingredients.set(ingredient_ids)
        if allergen_ids is not None:
            instance.allergens.set(allergen_ids)
        instance.save()
        return instance
