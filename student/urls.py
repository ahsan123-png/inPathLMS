from django.urls import path
from .views import *

urlpatterns = [
    path('courses/enrolled-students/<int:course_id>/', EnrollmentStudentsView.as_view(), name='enrolled-students'),
    path('enrolled-courses/<int:student_id>/', EnrolledCoursesAPIView.as_view(), name='enrolled_courses'),
    path('enroll-multiple-courses/', MultiCourseEnrollmentView.as_view(), name='enroll_multiple_courses'),
    path('create/profile/', StudentProfileView.as_view(), name='student_profile_list_create'), 
    path('upload-profile-picture/', ProfilePictureUploadView.as_view(), name='upload_profile_picture'),
]
