from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..models import CartItem
from ..serializers import CartItemSerializer
class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return (
            CartItem.objects
            .filter(user=self.request.user)
            .select_related("product")
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            quantity=1
        )
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response(
            {"detail": "Cart cleared"},
            status=status.HTTP_204_NO_CONTENT
        )
