import boto3
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import *
import random
from userEx.models import *
import re
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
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
        user_id = request.data.get('user_id')
        profile_picture = request.FILES.get('profile_picture')
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
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        file_name = os.path.basename(profile_picture.name)
        file_key = f"instructor_profiles/{file_name}"
        try:
            s3.upload_fileobj(profile_picture, settings.AWS_STORAGE_BUCKET_NAME, f"media/{file_key}",ExtraArgs={'ACL': 'public-read', 'ContentType': profile_picture.content_type})
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{file_key}"
            profile.profile_picture = file_url
            profile.save()
            return JsonResponse({
                "user_id": user.id,
                "profile_picture_url": file_url
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# =================== upload to S3 =================
# def upload_to_s3(file, course_title, file_type):
#     unique_id = uuid.uuid4().hex[:8]  # Generates a unique 8-character ID
#     course_title_safe = re.sub(r'\W+', '_', course_title).lower()
#     file_name = f"{course_title_safe}_{unique_id}.{file.name.split('.')[-1]}"
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#         region_name=settings.AWS_S3_REGION_NAME
#     )
#     bucket_name = settings.AWS_STORAGE_BUCKET_NAME
#     file_key = f"media/{file_type}/{file_name}"  # Path in S3
#     try:
#         s3_client.upload_fileobj(file, bucket_name, file_key, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
#     except Exception as e:
#         raise ValidationError(f"File upload to S3 failed: {str(e)}")
#     file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
def upload_to_s3(file, folder):
    s3 = boto3.client('s3')
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_path = f"{folder}/{file.name}"
    s3.upload_fileobj(
        file,
        bucket_name,
        file_path,
        ExtraArgs={'ACL': 'public-read','ContentType': file.content_type}
    )
    return file_path 
# =================== get instructors =================
def get_instructor(user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValidationError("Instructor with the given ID does not exist")
    if user.userrole.role != 'instructor':
        raise ValidationError("Only instructors can create courses or add content")
    return user
# ============== course Create View set =================
class CourseCreateAPIView(APIView):
    def list(self, request):
        lectures = Lecture.objects.all()
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # Retrieve a single lecture
    def retrieve(self, request, pk=None):
        try:
            lecture = Lecture.objects.get(pk=pk)
            serializer = LectureSerializer(lecture)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecture.DoesNotExist:
            return Response({"error": "Lecture not found"}, status=status.HTTP_404_NOT_FOUND)
    def create(self, request):
        section = request.data.get('section')
        title = request.data.get('title')
        order = request.data.get('order')
        video_file = request.FILES.get('video_file')
        if not all([section, title, order, video_file]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        file_path = upload_to_s3(video_file, 'lectures')
        # Save the lecture instance in the database
        lecture = Lecture.objects.create(
            section_id=section,
            title=title,
            order=order,
            video_file=file_path
        )
        serializer = LectureSerializer(lecture)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
# ============== upload contents like video or document ============

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    def get_serializer_class(self):
        return SectionSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user_id = self.request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        if course.instructor != user:
            raise ValidationError("Only the instructor of the course can add sections")
        serializer.save()


class LectureViewSet(viewsets.ViewSet):
    # Retrieve all lectures
    def list(self, request):
        lectures = Lecture.objects.all()
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # Retrieve a single lecture
    def retrieve(self, request, pk=None):
        try:
            lecture = Lecture.objects.get(pk=pk)
            serializer = LectureSerializer(lecture)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Lecture.DoesNotExist:
            return Response({"error": "Lecture not found"}, status=status.HTTP_404_NOT_FOUND)
    # Upload a new lecture (with file upload)
    def create(self, request):
        section = request.data.get('section')
        title = request.data.get('title')
        order = request.data.get('order')
        video_file = request.FILES.get('video_file')
        if not all([section, title, order, video_file]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        file_path = upload_to_s3(video_file, 'lectures')
        lecture = Lecture.objects.create(
            section_id=section,
            title=title,
            order=order,
            video_file=file_path
        )
        serializer = LectureSerializer(lecture)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
# =================== Assessment upload =================
class AssignmentViewSet(APIView):
    def post(self, request, *args, **kwargs):
        section_id = request.data.get('section_id')
        title = request.data.get('title')
        order = request.data.get('order')
        description = request.data.get('description')
        file = request.FILES.get('file')  # Ensure file is coming from FILES
        if not title or not description or not file or not section_id:
            raise ValidationError("title, description, and file must be provided")
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            raise ValidationError("Section not found")
        file_path = self.generate_file_path(title, file.name)
        file_url = self.upload_to_s3(file, file_path)
        assignment = Assignment.objects.create(
            section=section,
            title=title,
            description=description,
            doc_files=file_url  # Store S3 URL, not file path
        )
        return Response({
            "section": section.id,
            "message": "Assignment created successfully",
            "assignment": {
                "title": assignment.title,
                "doc_files": assignment.doc_files  # Return S3 URL
            }
        })
    def upload_to_s3(self, file, file_path):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        try:
            s3.upload_fileobj(
                file,
                bucket_name,
                file_path,
                ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
            )
        except Exception as e:
            raise ValidationError(f"File upload to S3 failed: {str(e)}")
        file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        return file_url
    def generate_file_path(self, title, file_name):
        unique_id = uuid.uuid4().hex[:8]
        sanitized_title = re.sub(r'\W+', '_', title).lower()
        sanitized_file_name = re.sub(r'\W+', '_', file_name).lower()
        file_extension = file_name.split('.')[-1] 
        return f"assignments/{sanitized_title}_{unique_id}.{file_extension}"
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

# ============== get all courses by instructor id ==============
class CourseByInstructorIdView(APIView):
    def get(self, request, instructor_id):
        courses = Course.objects.filter(instructor_id=instructor_id)
        if not courses.exists():
            return Response({"error": "No courses found with this instructor ID."}, status=status.HTTP_404_NOT_FOUND)
        serializers = CourseSerializer(courses, many=True)
        return Response(serializers.data)
    
# ================== Get all sections with course iD =================
class CourseSectionsView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.only('id', 'title').get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({"error": "Course not found."}, status=404)

        sections = Section.objects.filter(course=course).prefetch_related(
            'lectures', 'assignment'
        ).order_by('order')

        data = {
            'course_id': course.id,
            'course_title': course.title,
            'sections': [
                {
                    'section_id': section.id,
                    'section_title': section.title,
                    'order': section.order,
                    'lectures': [
                        {
                            'lecture_id': lecture.id,
                            'lecture_title': lecture.title,
                            'order': lecture.order,
                            'video_file': lecture.video_file.url if lecture.video_file else None
                        }
                        for lecture in section.lectures.all().order_by('order')
                    ],
                    'assignments': [
                        {
                            'assignment_id': assignment.id,
                            'assignment_title': assignment.title,
                            'description': assignment.description,
                            'doc_files': assignment.doc_files.url if assignment.doc_files else None
                        }
                        for assignment in section.assignment.all().order_by('id')
                    ]
                }
                for section in sections
            ]
        }
        return JsonResponse(data, status=200)