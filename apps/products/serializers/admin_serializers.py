import json
from rest_framework import serializers
from apps.products.models import Product, Category, Ingredient, Allergen, City, Nutrition


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"

class AllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergen
        fields = "__all__"

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"

class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ("calories", "protein", "fat", "carbs", "sugar")


class AdminProductSerializer(serializers.ModelSerializer):
    nutrition = NutritionSerializer(required=False)
    category_details = AdminCategorySerializer(source="category", read_only=True)
    
    # For writing (lists of IDs)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), many=True, required=False
    )
    allergens = serializers.PrimaryKeyRelatedField(
        queryset=Allergen.objects.all(), many=True, required=False
    )
    available_cities = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "currency", "category", "category_details",
            "image", "ingredients", "allergens", "available_cities", "description",
            "story", "average_rating", "review_count", "stock", "is_active",
            "nutrition", "created_at", "updated_at"
        ]
        read_only_fields = (
            "slug",
            "average_rating",
            "review_count",
            "created_at",
            "updated_at",
        )

    def to_internal_value(self, data):
        # Multipart data (QueryDict) + Windows + Files = Pickle Error on .copy()
        mutable_data = {}

        if hasattr(data, 'getlist'):
            for key in data:
                # 🛑 CRITICAL: Always treat these as lists for M2M fields
                if key in ['ingredients', 'allergens', 'available_cities']:
                    mutable_data[key] = data.getlist(key)
                else:
                    values = data.getlist(key)
                    if not values:
                        continue
                    
                    val = values[0]
                    # 🧩 Handle Boolean strings from FormData
                    if isinstance(val, str):
                        if val.lower() == 'true':
                            val = True
                        elif val.lower() == 'false':
                            val = False
                    
                    mutable_data[key] = val
        else:
             mutable_data = data.copy()

        # Parse Nutrition JSON string if present
        if "nutrition" in mutable_data and isinstance(mutable_data["nutrition"], str):
             try:
                  mutable_data["nutrition"] = json.loads(mutable_data["nutrition"])
             except (ValueError, TypeError):
                  pass
                  
        return super().to_internal_value(mutable_data)

    def create(self, validated_data):
        nutrition_data = validated_data.pop("nutrition", None)
        ingredients = validated_data.pop("ingredients", [])
        allergen_ids = validated_data.pop("allergens", [])
        city_ids = validated_data.pop("available_cities", [])

        product = Product.objects.create(**validated_data)
        
        product.ingredients.set(ingredients)
        product.allergens.set(allergen_ids)
        product.available_cities.set(city_ids)

        if nutrition_data:
            Nutrition.objects.create(product=product, **nutrition_data)

        return product

    def update(self, instance, validated_data):
        # 🟢 Extract nested/M2M data
        nutrition_data = validated_data.pop("nutrition", None)
        ingredients = validated_data.pop("ingredients", None)
        allergens = validated_data.pop("allergens", None)
        available_cities = validated_data.pop("available_cities", None)

        # 🚀 Update standard fields (stock, price, category, etc.)
        instance = super().update(instance, validated_data)

        # 🔗 Update M2M fields if provided
        if ingredients is not None:
            instance.ingredients.set(ingredients)
        if allergens is not None:
            instance.allergens.set(allergens)
        if available_cities is not None:
            instance.available_cities.set(available_cities)

        # 🥗 Update or Create Nutrition
        if nutrition_data:
            Nutrition.objects.update_or_create(
                product=instance,
                defaults=nutrition_data
            )

        return instance
