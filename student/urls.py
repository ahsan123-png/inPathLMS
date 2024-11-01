from django.urls import path
from .views import *

urlpatterns = [
    path('student/profile/', StudentProfileView.as_view(), name='student_profile_list_create'),  # GET all and POST (create)
    path('student/profile/<int:pk>/', StudentProfileView.as_view(), name='student_profile_detail'),  # GET by ID, PUT (update), DELETE
]
