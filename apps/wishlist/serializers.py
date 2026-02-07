from rest_framework import serializers
from .models import WishlistItem
from apps.products.models import Product
from apps.products.serializers.user_serializers import ProductSerializer
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source="product",
        write_only=True
    )
    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_id", "created_at"]
        read_only_fields = ["created_at"]