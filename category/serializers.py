from rest_framework import serializers
from userEx.models import *
# Base Serializer
class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
# Category Serializer
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'discount_percentage', 'thumbnail', 'intro_video']

# Updated SubCategory Serializer
class SubCategorySerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, source='course_set', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'courses']

# Updated Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, source='subcategory_set', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']
