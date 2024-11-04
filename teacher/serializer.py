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

    
