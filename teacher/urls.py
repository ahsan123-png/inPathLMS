from django.urls import path
from .views import *

urlpatterns = [
    #create profile
    path('instructor-profile/create/', InstructorProfileCreateView.as_view(), name='create_instructor_profile'),
    #crud
    path('instructor/profile/', InstructorProfileView.as_view(), name='instructor_profile_list_create'),
    path('instructor/profile/<int:pk>/', InstructorProfileView.as_view(), name='instructor_profile_detail'),
]
