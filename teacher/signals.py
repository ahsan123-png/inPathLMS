# myapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from userEx.models import InstructorProfile, UserRole
from .views import InstructorProfileCreateView


@receiver(post_save, sender=User)
def create_instructor_profile(sender, instance, created, **kwargs):
    if created:
        # Check if the user has the 'instructor' role
        try:
            user_role = UserRole.objects.get(user=instance)
            if user_role.role == 'instructor':
                # Create an InstructorProfile for the new instructor user
                InstructorProfile.objects.create(user=instance)
        except UserRole.DoesNotExist:
            pass  # If the user does not have a role, we do nothing
