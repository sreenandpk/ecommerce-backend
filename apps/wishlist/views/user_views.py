from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import WishlistItem
from ..serializers import WishlistSerializer
class WishlistView(ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return WishlistItem.objects.filter(
            user=self.request.user
        ).select_related("product")
    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        WishlistItem.objects.get_or_create(
            user=self.request.user,
            product=product
        )
class WishlistDeleteView(DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)