from django.urls import path
from .views import *

urlpatterns = [
    path('student/profile/', StudentProfileView.as_view(), name='student_profile_list_create'), 
    path('student/profile/<int:pk>/', StudentProfileView.as_view(), name='student_profile_detail'), 
    path('courses/enrolled-students/<int:course_id>/', EnrollmentStudentsView.as_view(), name='enrolled-students'),
    path('courses/enrolled-students/<int:course_id>/', EnrollmentStudentsView.as_view(), name='enrolled-students'),
    path('enrolled-courses/<int:student_id>/', EnrolledCoursesAPIView.as_view(), name='enrolled_courses'),
    path('enroll-multiple-courses/', MultiCourseEnrollmentView.as_view(), name='enroll_multiple_courses'),
]
