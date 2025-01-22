from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from userEx.models import User, Course, Wishlist
from .serializers import WishlistSerializer
from django.db import transaction
# ================== Views =================

class AddToWishlist(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.select_related('userrole').get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if user.userrole.role != 'student':
            return Response({"detail": "User is not a student."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        if Wishlist.objects.filter(user=user, course=course).exists():
            return Response({"detail": "Course already in your wishlist."}, status=status.HTTP_400_BAD_REQUEST)
        wishlist_item = Wishlist.objects.create(user=user, course=course)
        return Response(WishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)
# ==================== remove from wishlist ====================
class RemoveFromWishlist(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({"detail": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        wishlist_item = Wishlist.objects.filter(user=user, course=course).first()
        if not wishlist_item:
            return Response({"detail": "Course not found in your wishlist"}, status=status.HTTP_400_BAD_REQUEST)
        wishlist_item.delete()
        return Response({"detail": "Course removed from wishlist"}, status=status.HTTP_200_OK)
# ================= view wishlist ==============
from rest_framework.generics import ListAPIView
class WishlistView(ListAPIView):
    serializer_class = WishlistSerializer
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if not user_id:
            return Response({"detail": "Invalid or missing user_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Wishlist.objects.filter(user=user)
# ================== add to Cart ===============
class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")
        user = get_object_or_404(User.objects.select_related('userrole'), id=user_id)
        if user.userrole.role != 'student':
            return Response({"error": "User is not a student"}, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(Course, id=course_id)
        with transaction.atomic():
            cart_item, created = Cart.objects.get_or_create(user=user, course=course)
        course_details = {
            "course_id": course.id,
            "title": course.title,
            "description": course.description,
            "price": str(course.price)  
        }
        if created:
            return Response({
                "message": "Course added to cart",
                "course_details": course_details
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Course already in cart",
                "course_details": course_details
            }, status=status.HTTP_200_OK)

# ============= Remove course from cart ==============
class RemoveFromCartView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")
        user = get_object_or_404(User, id=user_id)
        if not hasattr(user, 'userrole') or user.userrole.role != 'student':
            return Response({"error": "User is not a student"}, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(Course, id=course_id)
        try:
            cart_item = Cart.objects.get(user=user, course=course)
            cart_item.delete()
            return Response({"message": "Course removed from cart"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Course not found in cart"}, status=status.HTTP_404_NOT_FOUND)