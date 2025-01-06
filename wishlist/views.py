from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from userEx.models import User, Course, Wishlist
from .serializers import WishlistSerializer
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
