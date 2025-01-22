from django.urls import path
from .views import *

urlpatterns = [
    path('add/', AddToWishlist.as_view(), name='add_to_wishlist'),
    path('remove/', RemoveFromWishlist.as_view(), name='remove_from_wishlist'),
    path('view/<int:user_id>/', WishlistView.as_view(), name='view_wishlist'),
    path('add_to_cart/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove_from_cart/', RemoveFromCartView.as_view(), name='remove_from_cart'),
]
