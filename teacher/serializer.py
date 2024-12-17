from rest_framework import serializers
from userEx.models import *
#===========================++++++++++++++++++++++++++++++++++
class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['user', 'bio', 'degrees', 'teaching_experience', 'specialization', 'teaching_history', 'profile_picture']
        # read_only_fields = ['user']
    def create(self, validated_data):
        user = validated_data['user']
        if InstructorProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("A profile for this user already exists.")
        return super().create(validated_data)
    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', instance.bio)
        instance.degrees = validated_data.get('degrees', instance.degrees)
        instance.teaching_experience = validated_data.get('teaching_experience', instance.teaching_experience)
        instance.specialization = validated_data.get('specialization', instance.specialization)
        instance.teaching_history = validated_data.get('teaching_history', instance.teaching_history)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance

# ============ Serializer for Course =====================
class CourseSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = "__all__"
    def get_final_price(self, obj):
        return obj.get_discounted_price()


# Serializer for Section
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

# Serializer for Lecture
class LectureSerializer(serializers.ModelSerializer):
    video_file_url = serializers.SerializerMethodField()
    class Meta:
        model = Lecture
        fields = ['id', 'section', 'title', 'video_file', 'video_file_url']
    def get_video_file_url(self, obj):
        return obj.video_file_url

# Serializer for Quiz
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

# Serializer for Question
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

# Serializer for Assignment
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

# Serializer for Feedback
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'course', 'user', 'rating', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

# Serializer for Enrollment (to manage course enrollment for students)
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'
