from rest_framework import serializers
from userEx.models import *
#===========================++++++++++++++++++++++++++++++++++
class InstructorProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = InstructorProfile
        fields = ['user_id', 'bio', 'degrees', 'teaching_experience', 'specialization', 'teaching_history', 'profile_picture','full_name']
        # read_only_fields = ['user']
    def get_full_name(self, obj):
    # Access the related User object and return the full name
        return f"{obj.user.first_name} {obj.user.last_name}"
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
    pass



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
        fields = '__all__'

# Serializer for Enrollment (to manage course enrollment for students)
class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'

class InstructorDetailSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
    def get_profile(self, obj):
        try:
            profile = InstructorProfile.objects.get(user=obj)
            return {
                'bio': profile.bio,
                'degrees': profile.degrees,
                'teaching_experience': profile.teaching_experience,
                'specialization': profile.specialization,
                'teaching_history': profile.teaching_history,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None
            }
        except InstructorProfile.DoesNotExist:
            return None