
from rest_framework.views import APIView
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from userEx.models import *
from .serializers import *
# ====================== Views ======================
# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
# ========== SubCategory ViewSet ==============
class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    # permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
class SubCategoryByCategoryAPIView(APIView):
    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
            subcategories = SubCategory.objects.filter(category=category)
            if not subcategories.exists():
                return JsonResponse(
                    {"detail": "No subcategories found for this category."}, 
                    status=404 
                )
            serializer = SubCategorySerializer(subcategories, many=True)
            return JsonResponse(
                serializer.data, 
                status=200, 
                safe=False 
            )
        except Category.DoesNotExist:
            return JsonResponse(
                {"detail": "Category not found."},
                status=404  # Status 404 Not Found
            )
