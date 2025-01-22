from rest_framework import serializers
from userEx.models import Wishlist , Cart
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

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'course']
        
    def validate(self, data):
        # Ensure that the user is a student
        user = data.get('user')
        if not hasattr(user, 'userrole') or user.userrole.role != 'student':
            raise serializers.ValidationError("User is not a student")
        return data
class CartCourseSerializer(serializers.ModelSerializer):
    # Include the relevant course details in the serializer
    course_id = serializers.IntegerField(source='course.id')
    title = serializers.CharField(source='course.title')
    description = serializers.CharField(source='course.description')
    price = serializers.DecimalField(source='course.price', max_digits=10, decimal_places=2)
    class Meta:
        model = Cart
        fields = [
        'course_id',
        'title',
        'description',
        'price',
        
        ]