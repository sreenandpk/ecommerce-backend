from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.products.models import Product

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "product"], name="unique_user_product_cart")
        ]
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.email} → {self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return (self.product.price or 0) * self.quantity