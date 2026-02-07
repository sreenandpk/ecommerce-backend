from rest_framework import serializers
from ..models import Order, OrderItem


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    product_image = serializers.ImageField(
        source="product.image",
        read_only=True
    )
    product_price = serializers.DecimalField(
        source="price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "product_price",
            "quantity",
            "price",
            "subtotal",
        ]
        read_only_fields = fields  # admin cannot edit items
        

class AdminOrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )
    items = AdminOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_email",
            "full_name",
            "phone",
            "address",
            "city",
            "pincode",
            "total_amount",
            "status",
            "is_paid",
            "payment_id",
            "created_at",
            "items",
        ]

        # 🔐 LOCK FIELDS (VERY IMPORTANT)
        read_only_fields = [
            "id",
            "user_email",
            "full_name",
            "phone",
            "address",
            "city",
            "pincode",
            "total_amount",
            "created_at",
            "items",
        ]
