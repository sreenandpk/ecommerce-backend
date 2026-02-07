from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from ..models import Order, OrderItem
from ..serializers.user_serializers import OrderSerializer
from apps.cart.models import CartItem
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        user = request.user
        cart_items = CartItem.objects.select_related("product").filter(user=user)
        if not cart_items.exists():
            return Response(
                {"detail": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        full_name = request.data.get("full_name")
        phone = request.data.get("phone")
        address = request.data.get("address")
        city = request.data.get("city")
        pincode = request.data.get("pincode")
        if not all([full_name, phone, address, city, pincode]):
            return Response(
                {"detail": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            total_amount=Decimal("0.00"),
        )

        total_amount = Decimal("0.00")
        for item in cart_items:
            product = item.product
            quantity = item.quantity
            if product.stock < quantity:
                transaction.set_rollback(True)
                return Response(
                    {"detail": f"{product.name} has only {product.stock} left"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            price = product.price
            subtotal = price * quantity
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                subtotal=subtotal,
            )
            product.stock -= quantity
            product.save()
            total_amount += subtotal
        order.total_amount = total_amount
        order.save()
        cart_items.delete()
        return Response(
            {
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED
        )
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related("items__product").get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order, context={'request': request})
        return Response(serializer.data)
