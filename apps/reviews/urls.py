from django.urls import path
from apps.reviews.views.user_views import ReviewListCreateView, ReviewDetailView, CheckReviewEligibilityView
urlpatterns = [
    path(
        "products/<int:product_id>/reviews/",
        ReviewListCreateView.as_view(),
        name="product-reviews",
    ),
    path(
        "products/<int:product_id>/review-eligibility/",
        CheckReviewEligibilityView.as_view(),
        name="review-eligibility",
    ),
    path(
        "reviews/<int:pk>/",
        ReviewDetailView.as_view(),
        name="review-detail",
    ),
]
