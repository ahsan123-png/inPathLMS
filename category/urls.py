from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
"""The reason for using the DefaultRouter in the Django REST Framework (DRF) and registering the ViewSet with it is to 
automatically generate the appropriate URL patterns for your API endpoints without the need to manually specify each path.
 Let's break it down:"""

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubCategoryViewSet, basename='subcategory')

urlpatterns = [
    path('', include(router.urls)),
     path('get/subcategories/<int:category_id>/', SubCategoryByCategoryAPIView.as_view(), name='get_subcategories_by_category'),
]
