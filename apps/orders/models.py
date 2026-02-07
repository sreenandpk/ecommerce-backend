from django.db import models
from django.conf import settings
from apps.products.models import Product
from decimal import Decimal
User = settings.AUTH_USER_MODEL
class Order(models.Model):
    STATUS_CHOICES = (
        ("awaiting_payment", "Awaiting Payment"),
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("paid", "Paid (Legacy)"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    total_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=Decimal("0.00") 
)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="awaiting_payment"
    )
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"Order #{self.id} - {self.user}"
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    ) 
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
