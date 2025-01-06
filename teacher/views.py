import json
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
from category.serializers import *
from userEx.models import *
import re
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from datetime import datetime
from django.utils.timezone import make_aware
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
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
            profile = serializer.save()
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
        user.delete()  
        return JsonResponse({"message": "Instructor profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
# =============== S3 uploads =================
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
    def parse_discount_end_date(self, discount_end_date):
        try:
            return make_aware(datetime.strptime(discount_end_date, '%Y-%m-%dT%H:%M:%SZ'))
        except ValueError:
            try:
                return make_aware(datetime.strptime(discount_end_date, '%Y-%m-%d'))
            except ValueError:
                raise ValidationError(
                )
    def generate_file_path(self, directory, file_name):
        # Generate a unique file path for storing in S3
        unique_id = uuid.uuid4().hex[:8]
        sanitized_file_name = re.sub(r'\s+', '_', file_name) 
        sanitized_file_name = re.sub(r'\W+', '_', sanitized_file_name) 
        file_extension = file_name.split('.')[-1] 
        file_path = f"{directory}/{unique_id}_{sanitized_file_name.lower()}"
        return file_path
    def upload_to_s3(self, file, file_path):
        # Initialize the S3 client
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
        # Generating the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_path}"
        return s3_url
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        instructor = request.data.get('instructor')
        category = request.data.get('category')
        subcategory = request.data.get('subcategory')
        price = request.data.get('price')
        discount_percentage = request.data.get('discount_percentage', 0)
        discount_end_date = request.data.get('discount_end_date')
        published = request.data.get('published', False)
        thumbnail = request.FILES.get('thumbnail')
        intro_video = request.FILES.get('intro_video')
        discount_percentage = Decimal(discount_percentage)
        price = Decimal(price)
        if discount_end_date:
            try:
                if 'T' not in discount_end_date:
                    discount_end_date += 'T00:00:00Z'  # Default to midnight
                discount_end_date_obj = make_aware(
                    datetime.strptime(discount_end_date, '%Y-%m-%dT%H:%M:%SZ')
                )
            except ValueError:
                return Response({"error": "Invalid discount_end_date format. Use ISO 8601 format (e.g., 2024-12-31T23:59:59Z)."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                discount_end_date_obj = None
        if not all([title, description, instructor, category, price]):
            return Response({"error": "All required fields must be provided."}, status=status.HTTP_400_BAD_REQUEST)
            discount_end_date_obj = None
        if discount_end_date:
            try:
                discount_end_date_obj = make_aware(
                    datetime.strptime(discount_end_date, '%Y-%m-%dT%H:%M:%SZ')
                )
            except ValueError:
                return Response({"error": "Invalid discount_end_date format. Use ISO 8601 format (e.g., 2024-12-31T23:59:59Z)."},
                                status=status.HTTP_400_BAD_REQUEST)
        if thumbnail:
            thumbnail_file_path = self.generate_file_path('courses', thumbnail.name)
            thumbnail_url = self.upload_to_s3(thumbnail, thumbnail_file_path)
        else:
            thumbnail_url = None
        if intro_video:
            intro_video_file_path = self.generate_file_path('lectures', intro_video.name)
            intro_video_url = self.upload_to_s3(intro_video, intro_video_file_path)
        else:
            intro_video_url = None
        course = Course.objects.create(
            title=title,
            description=description,
            instructor_id=instructor,
            category_id=category,
            subcategory_id=subcategory,
            price=price,
            discount_percentage=discount_percentage,
            discount_end_date=discount_end_date_obj,
            published=published,
            thumbnail=thumbnail_url,
            intro_video=intro_video_url
        )
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
# ============== Complete Course =============================
class CompleteCourseAPIView(APIView):
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            course.published = True
            course.save()
            return Response({"message": "Course marked as published successfully"}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
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
            raise ValidationError("All fields are required: title, description, file, and section_id")

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
            doc_files=file_url
        )
        return Response({
            "section": section.id,
            "message": "Assignment created successfully",
            "assignment": {
                "title": assignment.title,
                "doc_files": assignment.doc_files 
            }
        })
    def upload_to_s3(self, file, file_path):
        # Initialize the S3 client
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
        # Generate a unique file path for storing in S3
        unique_id = uuid.uuid4().hex[:8]
        sanitized_title = re.sub(r'\W+', '_', title).lower()
        sanitized_file_name = re.sub(r'\W+', '_', file_name).lower()
        file_extension = file_name.split('.')[-1] 
        return f"assignments/{sanitized_title}_{unique_id}.{file_extension}"
# ============= Feedback =============================
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        user = self.request.user
        if user.userrole.role != 'student':
            raise ValidationError("Only students can give feedback")
        serializer.save()
# ================== Enrollment =================================
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
                            'video_file': lecture.video_file_url
                        }
                        for lecture in section.lectures.all().order_by('order')
                    ],
                    'assignments': [
                        {
                            'assignment_id': assignment.id,
                            'assignment_title': assignment.title,
                            'description': assignment.description,
                            'doc_files': assignment.doc_files
                        }
                        for assignment in section.assignment.all().order_by('id')
                    ]
                }
                for section in sections
            ]
        }
        return JsonResponse(data, status=200)
# ================ Get all courses by subcategory id =================
class CourseListBySubCategoryView(APIView):
    def get(self, request, subcategory_id):
        courses = Course.objects.filter(subcategory_id=subcategory_id).select_related('category', 'subcategory', 'instructor')
        if not courses.exists():
            return Response({"detail": "No courses found for this subcategory."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# ============ Enrollment course ===================
class EnrollStudentAPIView(APIView):
    def post(self, request, course_id):
        try:
            data=json.loads(request.body)
            user_id = data.get('user')
            user = User.objects.get(id=user_id)
            user_role = UserRole.objects.filter(user=user).first()
            if not user_role or user_role.role != 'student':
                return Response({"error": "Only students can enroll in courses."}, status=status.HTTP_403_FORBIDDEN)
            course = get_object_or_404(Course, id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
            if not created:
                return Response({"message": "You are already enrolled in this course."}, status=status.HTTP_200_OK)
            return Response({"message": "Enrollment successful!",
                            "enrollment_id":enrollment.id }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ================== Get All students By enrollment id =================
# class GetStudentsByEnrollmentID(APIView):
#     def get(self, request, enrollment_id):
#         try:
#             enrollment = Enrollment.objects.get(id=enrollment_id)
#             students = User.objects.filter(id=enrollment.student.id)
#             serializer = UserSerializer(students, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Enrollment.DoesNotExist:
#             return Response({"detail": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ================== get all data of courses =================
class CetegoryCourseAPIView(APIView):
    def get(self, request):
        cetegories = Category.objects.prefetch_related(
            Prefetch(
                'subcategory_set',
                queryset=SubCategory.objects.prefetch_related(
                    Prefetch('course_set', queryset=Course.objects.filter(is_approved=False, published=False))
                )
            )
        )
        serializer = CategorySerializer(cetegories, many=True)
        return Response(serializer.data)
# ================ Approve Course ===================
class CourseApprovalAPIView(APIView):
    def patch(self, request, course_id):
        # Ensure the user is an admin
        # if not request.user.userrole.role == 'admin':
        #     raise PermissionDenied("You do not have permission to approve courses.")
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        course.is_approved = True
        course.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
# =================== CURD teacher details ==================
class InstructorDetailView(APIView):
    def get(self, request, user_id=None):
        if user_id:
            try:
                user = User.objects.get(id=user_id, userrole__role='instructor')
                profile = InstructorProfile.objects.filter(user=user).first()
                data = {
                    "user": {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    },
                    "profile": {
                        "bio": profile.bio if profile else None,
                        "degrees": profile.degrees if profile else None,
                        "teaching_experience": profile.teaching_experience if profile else None,
                        "specialization": profile.specialization if profile else None,
                        "teaching_history": profile.teaching_history if profile else None,
                        "profile_picture": profile.profile_picture if profile and profile.profile_picture else None
                    }
                }
                return Response(data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Instructor not found"}, status=status.HTTP_404_NOT_FOUND)
        instructors = User.objects.filter(userrole__role='instructor').select_related('userrole')
        serializer = InstructorDetailSerializer(instructors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, userrole__role='instructor')
            profile, created = InstructorProfile.objects.get_or_create(user=user)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            user.email = request.data.get('email', user.email)
            user.save()
            profile.bio = request.data.get('bio', profile.bio)
            profile.degrees = request.data.get('degrees', profile.degrees)
            profile.teaching_experience = request.data.get('teaching_experience', profile.teaching_experience)
            profile.specialization = request.data.get('specialization', profile.specialization)
            profile.teaching_history = request.data.get('teaching_history', profile.teaching_history)
            profile.profile_picture = request.data.get('profile_picture', profile.profile_picture)
            profile.save()
            user_data = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
            profile_data = {
                "bio": profile.bio,
                "degrees": profile.degrees,
                "teaching_experience": profile.teaching_experience,
                "specialization": profile.specialization,
                "teaching_history": profile.teaching_history,
                "profile_picture": profile.profile_picture if profile.profile_picture else None
            }
            return Response({
                "message": "Instructor details updated successfully",
                "user": user_data,
                "profile": profile_data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Instructor not found"}, status=status.HTTP_404_NOT_FOUND)
