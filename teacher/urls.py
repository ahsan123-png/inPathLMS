from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'sections', SectionViewSet)
router.register(r'lectures', LectureViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'enrollments', EnrollmentViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    #create profile
    path('profile/create/', InstructorProfileCreateView.as_view(), name='create_instructor_profile'),
    #crud
    path('all/profile/', InstructorProfileView.as_view(), name='instructor_profile_list_create'),
    path('profile/<int:pk>/', InstructorProfileView.as_view(), name='instructor_profile_detail'),
]