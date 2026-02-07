from rest_framework import serializers
from ..models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    product_image = serializers.ImageField(
        source="product.image",
        read_only=True
    )
    product_slug = serializers.SlugField(
        source="product.slug",
        read_only=True
    )

    # Snapshot price (order-time price)
    product_price = serializers.DecimalField(
        source="price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    # ⭐ Live product review data
    average_rating = serializers.FloatField(
        source="product.average_rating",
        read_only=True
    )
    review_count = serializers.IntegerField(
        source="product.review_count",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "product_slug",
            "product_price",
            "quantity",
            "subtotal",
            "average_rating",
            "review_count",
        ]



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "phone",
            "address",
            "city",
            "pincode",
            "total_amount",
            "status",
            "is_paid",
            "created_at",
            "shipped_at",
            "items",
        ]
        read_only_fields = [
            "total_amount",
            "status",
            "is_paid",
            "created_at",
        ]

    def validate_phone(self, value):
        if not value or len(value) < 10:
            raise serializers.ValidationError(
                "Enter a valid phone number"
            )
        return value

    def validate_city(self, value):
        if not value:
            raise serializers.ValidationError(
                "City is required"
            )
        return value

    def validate_pincode(self, value):
        if not value:
            raise serializers.ValidationError(
                "Pincode is required"
            )
        return value
