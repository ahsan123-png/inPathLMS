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
def upload_to_s3(file, course_title, file_type):
    unique_id = uuid.uuid4().hex[:8]  # Generates a unique 8-character ID
    course_title_safe = re.sub(r'\W+', '_', course_title).lower()
    file_name = f"{course_title_safe}_{unique_id}.{file.name.split('.')[-1]}"
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_key = f"media/{file_type}/{file_name}"  # Path in S3
    try:
        s3_client.upload_fileobj(file, bucket_name, file_key, ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type})
    except Exception as e:
        raise ValidationError(f"File upload to S3 failed: {str(e)}")
    file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
    return file_url
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
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('instructor')
        if not user_id:
            raise ValidationError("Instructor ID must be provided")
        user = get_instructor(user_id)
        thumbnail = request.FILES.get('thumbnail')
        intro_video = request.FILES.get('intro_video')
        course_title = request.data.get('title')
        thumbnail_url = None
        intro_video_url = None
        if thumbnail:
            thumbnail_url = upload_to_s3(thumbnail, course_title, "thumbnails")
        if intro_video:
            intro_video_url = upload_to_s3(intro_video, course_title, "intro_video")
        course = Course.objects.create(
            instructor=user,
            title=request.data.get('title'),
            description=request.data.get('description'),
            price=request.data.get('price'),
            discount_percentage=request.data.get('discount_percentage'),
            discount_end_date=request.data.get('discount_end_date'),
            published=request.data.get('published', False),
            category_id=request.data.get('category'),
            subcategory_id=request.data.get('subcategory'),
            thumbnail=thumbnail_url,  
            intro_video=intro_video_url  
        )
        return Response({
            "id": course.id,
            "title": course.title,
            "thumbnail": thumbnail_url,
            "intro_video": intro_video_url,
        }, status=status.HTTP_201_CREATED)
# ============== upload contents like video or document ============
class UploadContentView(APIView):
    def post(self, request, *args, **kwargs):
        content_type = request.data.get('content_type')  # 'lecture' or 'assignment'
        section_id = request.data.get('section_id')
        title = request.data.get('title')
        file = request.FILES.get('file')
        if not content_type or not file or not section_id or not title:
            raise ValidationError("Content type, file, title, and section ID must be provided.")
        if content_type == 'lecture':
            instructor_id = request.data.get('instructor')
            if not instructor_id:
                raise ValidationError("Instructor ID must be provided.")
            return self.handle_lecture_upload(section_id, title, file, instructor_id)
        elif content_type == 'assignment':
            return self.handle_assignment_upload(section_id, title, file, request.user)
        else:
            raise ValidationError("Invalid content type. Must be 'lecture' or 'assignment'.")
    def handle_lecture_upload(self, section_id, title, file, instructor_id):
        section = get_object_or_404(Section, id=section_id)
        course = section.course
        if course.instructor.id != int(instructor_id):
            raise ValidationError("Only the instructor of the course can upload lectures.")
        next_order = section.lectures.count() + 1
        file_url = self.upload_to_s3(file, f"lectures/{course.id}/{section_id}/{title}")
        lecture = Lecture.objects.create(
            section=section,
            title=title,
            order=next_order,
            video_file=file_url
        )
        return Response({
            "message": "Lecture uploaded successfully.",
            "lecture_id": lecture.id,
            "section_id": section.id,
            "course_id": course.id,
            "file_url": lecture.video_file
        }, status=status.HTTP_201_CREATED)
    def handle_assignment_upload(self, section_id, title, file, user):
        section = get_object_or_404(Section, id=section_id)
        assignment = Assignment.objects.filter(course=section.course).first()
        if not assignment:
            raise ValidationError("No assignment found for the section's course.")
        file_url = self.upload_to_s3(file, f"assignments/{assignment.course.id}/{section_id}/{title}")
        assignment_submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            user=user,
            submission_file=file_url
        )
        return Response({
            "message": "Assignment submitted successfully.",
            "submission_id": assignment_submission.id,
            "section_id": section.id,
            "course_id": section.course.id,
            "file_url": assignment_submission.submission_file
        }, status=status.HTTP_201_CREATED)
    def upload_to_s3(self, file, file_path):
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3.upload_fileobj(
            file,
            bucket_name,
            file_path,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
        )
        file_url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_path}"
        return file_url
# =================================================================
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
class LectureViewSet(APIView):
    queryset = Lecture.objects.all()
    def perform_create(self, request, *args, **kwargs):
        section_id = request.data.get('section_id')
        title = request.data.get('title')
        instructor_id = request.data.get('instructor')
        file = request.data.get('file')
        if not section_id or not title or not instructor_id or not file:
            raise ValidationError("Section, title, instructor, and file must be provided")
        section = Section.objects.get(id=section_id)
        course = section.course
        instructor = get_instructor(instructor_id)
        if course.instructor != instructor:
            raise ValidationError("Only the instructor of the course can add lectures")
        file_url = upload_to_s3(file, course.title, 'lectures')
        lecture = Lecture.objects.create(
            section=section,
            title=title,
            instructor=instructor,
            file_url=file_url  # Assuming the model has a file_url field to store S3 URL
        )
        return Response({
            "message": "Lecture created successfully",
            "lecture": {"title": lecture.title, "file_url": lecture.file_url}
        })
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

class AssignmentViewSet(APIView):
    queryset = Assignment.objects.all()
    def perform_create(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        title = request.data.get('title')
        instructor_id = request.data.get('instructor')
        description = request.data.get('description')
        file = request.data.get('file')
        due_date = request.data.get('due_date')
        if not course_id or not title or not instructor_id or not description or not due_date or not file:
            raise ValidationError("Course, title, instructor, description, due_date, and file must be provided")
        course = Course.objects.get(id=course_id)
        instructor = get_instructor(instructor_id)
        if course.instructor != instructor:
            raise ValidationError("Only the instructor of the course can add assignments")
        file_url = upload_to_s3(file, course.title, 'assignments')
        assignment = Assignment.objects.create(
            course=course,
            title=title,
            description=description,
            due_date=due_date,
            file_url=file_url 
        )
        return Response({
            "message": "Assignment created successfully",
            "assignment": {"title": assignment.title, "file_url": assignment.file_url}
        })

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
            'lectures'
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
                    ]
                }
                for section in sections
            ]
        }
        return JsonResponse(data, status=200)
