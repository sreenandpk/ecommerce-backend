from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
User = settings.AUTH_USER_MODEL
class Review(models.Model):
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional review comment"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide review without deleting"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_per_product"
            )
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["user"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
    def __str__(self):
        return f"{self.user} → {self.product} ({self.rating}⭐)"
    @property
    def short_comment(self):
        if not self.comment:
            return "-"
        return self.comment[:40] + "..." if len(self.comment) > 40 else self.comment
