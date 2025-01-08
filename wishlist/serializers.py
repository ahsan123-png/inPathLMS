from rest_framework import serializers
from userEx.models import Wishlist
from rest_framework import serializers
# ================ serializer ================
class WishlistSerializer(serializers.ModelSerializer):
    wishlist_id = serializers.IntegerField(source='id', read_only=True)
    course = serializers.SerializerMethodField()
    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'user', 'course']
    def get_course(self, obj):
        return {
            "course_id": obj.course.id,
            "title": obj.course.title,
            "category": obj.course.category.name,
            "subcategory": obj.course.subcategory.name,
            "price": obj.course.price,
            "thumbnail": obj.course.thumbnail,
        }
