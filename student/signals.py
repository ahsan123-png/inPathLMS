# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

# Import inside the signal handler to avoid circular import
@receiver(post_save, sender='auth.User')
def create_student_profile(sender, instance, created, **kwargs):
    # Delayed import inside the function
    from userEx.models import StudentProfile

    if created:
        StudentProfile.objects.create(user=instance)
