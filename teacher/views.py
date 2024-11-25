from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import *
from userEx.models import *
from rest_framework.response import Response
from rest_framework import status
# =========== CBV ===================
#=============== Create Profile  ======================
class InstructorProfileCreateView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(user, 'userrole') or user.userrole.role != 'instructor':
            return Response({"error": "User does not have the 'instructor' role"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = InstructorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#============= Teacher CRUD =======================
class InstructorProfileView(APIView):
    def get_user_role(self, user):
        try:
            return UserRole.objects.get(user=user)
        except UserRole.DoesNotExist:
            return None
    def get(self, request, user_id=None):
        """Retrieve instructor profiles by user ID or list all instructors."""
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                user_role = self.get_user_role(user)
                if user_role is None or user_role.role != 'instructor':
                    return JsonResponse(
                        {"error": "The provided user ID does not belong to an instructor. Please provide a valid instructor ID."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                profile = InstructorProfile.objects.get(user=user)
                serializer = InstructorProfileSerializer(profile)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except InstructorProfile.DoesNotExist:
                return JsonResponse({"error": "Instructor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            profiles = InstructorProfile.objects.select_related('user').filter(user__userrole__role='instructor')
            serializer = InstructorProfileSerializer(profiles, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    def put(self, request, user_id):
        """Update an instructor profile by user ID."""
        try:
            user = User.objects.get(id=user_id)
            user_role = self.get_user_role(user)
            if user_role is None or user_role.role != 'instructor':
                return JsonResponse(
                    {"error": "The provided user ID does not belong to an instructor. Please provide a valid instructor ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            profile = InstructorProfile.objects.get(user=user)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"error": "Instructor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        # Handle password update
        if 'password' in data:
            old_password = data.get('old_password')
            new_password = data.get('password')
            if not user.check_password(old_password):
                return JsonResponse({"error": "The old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()
        # Update the profile using the serializer, excluding the user field
        serializer = InstructorProfileSerializer(profile, data=data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, user_id):
        """Delete an instructor profile by user ID."""
        try:
            user = User.objects.get(id=user_id)
            user_role = self.get_user_role(user)
            if user_role is None or user_role.role != 'instructor':
                return JsonResponse(
                    {"error": "The provided user ID does not belong to an instructor. Please provide a valid instructor ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            profile = InstructorProfile.objects.get(user=user)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"error": "Instructor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()  # Deletes the user and cascades to delete the profile
        return JsonResponse({"message": "Instructor profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
#============== Profile Image =============================
class UploadProfilePictureView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        """Upload or update the profile picture for the instructor."""
        user_id = request.data.get('user_id')
        profile_picture = request.data.get('profile_picture')
        if not user_id or not profile_picture:
            return JsonResponse({"error": "User ID and profile picture are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if not hasattr(user, 'userrole') or user.userrole.role != 'instructor':
            return JsonResponse({"error": "User does not have the 'instructor' role."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            profile = InstructorProfile.objects.get(user=user)
        except InstructorProfile.DoesNotExist:
            return JsonResponse({"error": "Instructor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        profile.profile_picture = profile_picture
        profile.save()
        serializer = InstructorProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
