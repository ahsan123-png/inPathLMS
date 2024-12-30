from django.apps import AppConfig
from . import signals


class StudentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'student'
    def ready(self):
        import student.signals
