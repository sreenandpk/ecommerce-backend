from django.urls import path
from apps.wishlist.views.user_views import WishlistView, WishlistDeleteView
urlpatterns = [
    path("wishlist/", WishlistView.as_view()),
    path("wishlist/<int:pk>/", WishlistDeleteView.as_view()),
]
