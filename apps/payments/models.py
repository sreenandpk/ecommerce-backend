# apps/payments/models.py
from django.db import models
from django.conf import settings
from apps.orders.models import Order
User = settings.AUTH_USER_MODEL
class Payment(models.Model):
    STATUS_CHOICES = (
        ("created", "Created"),
        ("success", "Success"),
        ("failed", "Failed"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment #{self.id} - {self.order.id}"
