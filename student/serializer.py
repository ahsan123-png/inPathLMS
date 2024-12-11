from rest_framework import serializers
from django.contrib.auth.models import User
from userEx.models import *
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
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"

# ================= muilti course serializer =================
class MultiCourseEnrollmentSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    course_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    def validate(self, data):
        user_id = data.get('user_id')
        course_ids = data.get('course_ids')
        # Check if user exists and has a student role
        if not user_id:
            raise serializers.ValidationError("User ID is required.")
        # Check if the user has the student role
        from django.contrib.auth.models import User
        user = User.objects.filter(id=user_id).first()
        if not user or user.userrole.role != 'student':
            raise serializers.ValidationError("User must be a student.")
        # Check if all courses exist
        for course_id in course_ids:
            if not Course.objects.filter(id=course_id).exists():
                raise serializers.ValidationError(f"Course with ID {course_id} does not exist.")
        return data
    def create(self, validated_data):
        user_id = validated_data.get('user_id')
        course_ids = validated_data.get('course_ids')
        enrollments = []
        for course_id in course_ids:
            enrollment, created = Enrollment.objects.get_or_create(
                user_id=user_id,
                course_id=course_id,
                defaults={'progress': 0.0}
            )
            enrollments.append(enrollment)
        return enrollments
