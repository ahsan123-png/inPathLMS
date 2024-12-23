from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
# router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
# router.register(r'lectures', LectureViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
# router.register(r'assignments', AssignmentViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'enrollments', EnrollmentViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    #create profile
    path('profile/create/', InstructorProfileCreateView.as_view(), name='create_instructor_profile'),
    #crud
    path('all/profile/', InstructorProfileView.as_view(), name='instructor_profile_list_create'),
    path('profile/<int:user_id>/', InstructorProfileView.as_view(), name='instructor_profile_detail'),
    path('upload-profile-picture/', UploadProfilePictureView.as_view(), name='upload_profile_picture'),
    path('get/courses/<int:instructor_id>', CourseByInstructorIdView.as_view(), name='CourseByInstructorIdView'),
    path('courses/sections/<int:course_id>', CourseSectionsView.as_view(), name='course_sections'),
    path('course/complete/<int:course_id>', CompleteCourseAPIView.as_view(), name='CompleteCourseAPIView'),
    path('api/courses/', CourseCreateAPIView.as_view(), name='CourseCreateAPIView'),
    path('lectures/', LectureViewSet.as_view({'get': 'list', 'post': 'create'}), name='lecture-create'),
    path('assignments/', AssignmentViewSet.as_view(), name='assignment-create'),
    path('courses_list/subcategory/<int:subcategory_id>', CourseListBySubCategoryView.as_view(), name='CourseListBySubCategoryView'),
    path('course/enrollment/<int:course_id>/', EnrollStudentAPIView.as_view(), name='EnrollStudentAPIView'),
    path('api/categories-courses/', CetegoryCourseAPIView.as_view(), name='categories-courses'),
    path('admin/course/approve/<int:course_id>/', CourseApprovalAPIView.as_view(), name='approve_course'),

]