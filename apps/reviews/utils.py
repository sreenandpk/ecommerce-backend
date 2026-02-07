from django.db.models import Avg, Count
from .models import Review
def update_product_rating(product):
    stats = Review.objects.filter(
        product=product,
        is_active=True
    ).aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id")
    )
    product.average_rating = stats["avg_rating"] or 0
    product.review_count = stats["total_reviews"]
    product.save(update_fields=["average_rating", "review_count"])
