from rest_framework import serializers
from userEx.models import Wishlist
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['user', 'course']

    def create(self, validated_data):
        return Wishlist.objects.create(**validated_data)

    def to_representation(self, instance):
        return {
            'course': instance.course.title,
            'course_id': instance.course.id,
            'course_description': instance.course.description
        }
