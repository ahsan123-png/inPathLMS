from rest_framework import serializers
from userEx.models import *
#===========================++++++++++++++++++++++++++++++++++
class InstructorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorProfile
        fields = ['bio', 'degrees', 'teaching_experience', 'specialization', 'teaching_history', 'profile_picture']
    def validate_user(self, user):
        try:
            user_role = UserRole.objects.get(user=user)
            if user_role.role != 'instructor':
                raise serializers.ValidationError("The provided user ID does not belong to a teacher. Please provide a valid Teacher ID.")
        except UserRole.DoesNotExist:
            raise serializers.ValidationError("The provided user ID does not have a role assigned.")
        return user
    def create(self, validated_data):
        user = validated_data.get('user')
        self.validate_user(user)
        bio = validated_data.get('bio', '')
        degrees = validated_data.get('degrees', '')
        teaching_experience = validated_data.get('teaching_experience', 0)
        specialization = validated_data.get('specialization', '')
        teaching_history = validated_data.get('teaching_history', '')
        profile_picture = validated_data.get('profile_picture', None)
        instructor_profile = InstructorProfile.objects.create(
            user=self.context['user'],
            bio=bio,
            degrees=degrees,
            teaching_experience=teaching_experience,
            specialization=specialization,
            teaching_history=teaching_history,
            profile_picture=profile_picture
        )
        return instructor_profile
    def update(self, instance, validated_data):
        # Updating each field
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
    class Meta:
        model = Course
        fields = '__all__'
    def validate_course(self, value):
        if not Course.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Course with the given ID does not exist.")
        return value

# Serializer for Section
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

# Serializer for Lecture
class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'

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
