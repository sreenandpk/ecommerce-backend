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
            is_paid=True
        ).exists()

        if not has_purchased:
             raise serializers.ValidationError(
                {"detail": "You can only review products you have purchased."}
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
