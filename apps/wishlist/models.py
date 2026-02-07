from django.db import models
from django.conf import settings
from apps.products.models import Product
class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_wishlist")
        ]
        indexes = [
            models.Index(fields=["user", "product"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]
    def __str__(self):
        user_email = getattr(self.user, "email", "Unknown User")
        product_name = getattr(self.product, "name", "Unknown Product")
        return f"{user_email} → {product_name}"