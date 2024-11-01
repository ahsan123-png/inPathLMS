from rest_framework import serializers
from django.contrib.auth.models import User

class StudentProfileSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()  # Add this to get the role

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role']  # Include 'role'

    def get_role(self, obj):
        user_role = getattr(obj, 'userrole', None)
        return user_role.role if user_role else None
    def update(self, instance, validated_data):
        # Update the student profile fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance
