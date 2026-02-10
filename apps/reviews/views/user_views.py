from django.db import models
from rest_framework.response import Response
from rest_framework import generics, permissions, serializers
from ..models import Review
from ..serializers import ReviewSerializer

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        return (
            Review.objects
            .filter(
                product_id=self.kwargs["product_id"],
                is_active=True
            )
            .select_related("user")
            .order_by("-created_at")
        )
    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.kwargs["product_id"]

        # Check if user has purchased the product
        from apps.orders.models import Order
        has_purchased = Order.objects.filter(
            user=user,
            items__product_id=product_id,
            is_paid=True,
            status="delivered"
        ).exists()

        if not has_purchased:
             raise serializers.ValidationError(
                {"detail": "You can only review products that have been delivered to you."}
            )

        if Review.objects.filter(
            user=user,
            product_id=product_id
        ).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this product."}
            )
        serializer.save(
            user=user,
            product_id=product_id
        )
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return (
            Review.objects
            .filter(
                user=self.request.user,
                is_active=True
            )
            .select_related("user", "product")
        )
class CheckReviewEligibilityView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        user = request.user
        from apps.orders.models import Order
        
        # 1. Total purchased check (Any non-cancelled order with this product)
        all_product_orders = Order.objects.filter(
            user=user,
            items__product_id=product_id
        ).exclude(status="cancelled")

        if not all_product_orders.exists():
            return Response({
                "eligible": False,
                "reason": "NOT_PURCHASED",
                "detail": "You can only review products that you have purchased."
            })

        # 2. Eligibility is granted if ANY such order is "delivered" OR "is_paid"
        eligible_orders = all_product_orders.filter(
            models.Q(status="delivered") | models.Q(is_paid=True)
        )

        if not eligible_orders.exists():
            # If we have an order but it's not paid/delivered yet
            current_status = all_product_orders.first().status
            return Response({
                "eligible": False,
                "reason": "NOT_DELIVERED",
                "detail": f"You can only review products after they are delivered. Current status: {current_status}"
            })
            
        # 3. If it's paid but user wants it only when delivered (as per instruction)
        # Let's check if there's a delivered one.
        delivered_orders = all_product_orders.filter(status="delivered")
        if not delivered_orders.exists():
             return Response({
                "eligible": False,
                "reason": "NOT_DELIVERED",
                "detail": "You can only review products that have been delivered to you."
            })

        # 4. Check if already reviewed
        already_reviewed = Review.objects.filter(
            user=user,
            product_id=product_id
        ).exists()

        if already_reviewed:
            return Response({
                "eligible": False,
                "reason": "ALREADY_REVIEWED",
                "detail": "You have already reviewed this product."
            })

        return Response({
            "eligible": True,
            "detail": "You are eligible to review this product."
        })
