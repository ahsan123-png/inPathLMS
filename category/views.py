
import requests
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from userEx.models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .scraper import scrape_trending_courses
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
    def perform_create(self, serializer):
        serializer.save(category_id=self.request.data.get('category'))
    
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
# ===================== Trending sKills =============================
class TrendingSkillsView(APIView):
    def get(self, request):
        try:
            urls='https://www.classcentral.com/report/most-popular-online-courses/'
            trending_skills = scrape_trending_courses(urls)
            return Response({"trending_skills": trending_skills}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

