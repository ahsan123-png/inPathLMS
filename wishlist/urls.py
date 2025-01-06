from django.urls import path
from .views import AddToWishlist, RemoveFromWishlist, WishlistView

urlpatterns = [
    path('add/', AddToWishlist.as_view(), name='add_to_wishlist'),
    path('remove/', RemoveFromWishlist.as_view(), name='remove_from_wishlist'),
    path('view/<int:user_id>/', WishlistView.as_view(), name='view_wishlist'),
]
