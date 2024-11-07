from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .serializer import *
from userEx.models import *
# =========== CBV ===================
#=============== Create Profile  ======================
# we have two ways to create profile 
# By APIView
# class InstructorProfileCreateView(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         serializer = InstructorProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Instructor profile created successfully", "profile": serializer.data}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#========= By CreateAPIView ====================
class InstructorProfileCreateView(CreateAPIView):
    queryset = InstructorProfile.objects.all()
    serializer_class = InstructorProfileSerializer
    # permission_classes = [IsAuthenticated]
#============= Teacher CRUD =======================
class InstructorProfileView(APIView):
    def get_user_role(self, user):
        try:
            return UserRole.objects.select_related('user').get(user=user)
        except UserRole.DoesNotExist:
            return None
    def get(self, request, pk=None):
        if pk:
            try:
                profile = InstructorProfile.objects.get(pk=pk)
                user_role = self.get_user_role(profile.user)
                if user_role is None or user_role.role != 'instructor':
                    return JsonResponse({"error": "The provided user ID does not belong to an instructor. Please provide a valid Instructor ID."},
                                        status=status.HTTP_400_BAD_REQUEST)
                serializer = InstructorProfileSerializer(profile)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except InstructorProfile.DoesNotExist:
                return JsonResponse({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            profiles = InstructorProfile.objects.select_related('user').filter(user__userrole__role='instructor')
            serializer = InstructorProfileSerializer(profiles, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    def put(self, request, pk):
        try:
            profile = InstructorProfile.objects.get(pk=pk)
            user_role = self.get_user_role(profile.user)
            if user_role is None or user_role.role != 'instructor':
                return JsonResponse({"error": "The provided user ID does not belong to an instructor. Please provide a valid Instructor ID."},
                                    status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            # Check if password needs to be updated
            if 'password' in data:
                old_password = data.get('old_password')
                new_password = data.get('password')
                if not profile.user.check_password(old_password):
                    return JsonResponse({"error": "The old password is incorrect. Please provide the correct password."}, status=status.HTTP_400_BAD_REQUEST)
                profile.user.set_password(new_password)
                profile.user.save()
            serializer = InstructorProfileSerializer(profile, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        try:
            profile = InstructorProfile.objects.get(pk=pk)
            user_role = self.get_user_role(profile.user)
            if user_role is None or user_role.role != 'instructor':
                return JsonResponse({"error": "The provided user ID does not belong to an instructor. Please provide a valid Instructor ID."},
                                    status=status.HTTP_400_BAD_REQUEST)
            profile.user.delete()
            return JsonResponse({"message": "Instructor profile deleted."}, status=status.HTTP_204_NO_CONTENT)
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)

def get_instructor(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValidationError("Instructor with the given ID does not exist")
    if user.userrole.role != 'instructor':
        raise ValidationError("Only instructors can create courses or add content")
    return user

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def perform_create(self, serializer):
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        serializer.save(instructor=user)

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add sections")
        serializer.save()

class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    def perform_create(self, serializer):
        section = serializer.validated_data['section']
        course = section.course
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add lectures")
        serializer.save()

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add quizzes")
        serializer.save()

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    def perform_create(self, serializer):
        quiz = serializer.validated_data['quiz']
        course = quiz.course
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add questions")
        serializer.save()

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add assignments")
        serializer.save()

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user = self.request.user
        if user.userrole.role != 'student':
            raise ValidationError("Only students can give feedback")
        serializer.save()

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data['course']
        if course.instructor == user:
            raise ValidationError("Instructors cannot enroll in their own course")
        serializer.save(user=user)
