import boto3
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.http import JsonResponse 
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import *
from userEx.models import *
# ============== CBV CURD =============== 
# ================= Get student details who enroll to a course =================
class EnrollmentStudentsView(APIView):
    def get(self, request, course_id):
        try:
            course=Course.objects.get(id=course_id)
            enrollments=Enrollment.objects.filter(course=course)
            enrolled_student = []
            for enrollment in enrollments:
                student=enrollment.user
                enrolled_student.append({
                    "id" : student.id,
                    "username" : student.username,
                    "email" : student.email,
                    "enrolled_at" : enrollment.enrolled_at,
                    "progress" : enrollment.progress,
                })
            return Response({
                "course": {
                    "id": course.id,
                    "title" : course.title,
                },
                "students" : enrolled_student,
                },status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error":"Course not found"}, status=status.HTTP_404_NOT_FOUND)
# ==================== get all enrolled courses student id =================
class EnrolledCoursesAPIView(APIView):    
    def get(self, request, student_id):
        try:
            enrollments = Enrollment.objects.filter(user_id=student_id)
            if not enrollments.exists():
                return Response({"message": "No enrolled courses found"}, status=status.HTTP_200_ok)
            courses = [enrollment.course for enrollment in enrollments]
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST) 

# ====================  enrolled more than one courses student id =================
class MultiCourseEnrollmentView(APIView):
    def post(self, request):
        serializer = MultiCourseEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            enrollments = serializer.save()
            return Response(
                {"message": f"Successfully enrolled in {len(enrollments)} courses."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ==================== student profile ====================
class StudentProfileView(APIView):
    def get(self, request, user_id=None):
        try:
            if user_id:
                user_profile = StudentProfile.objects.select_related(
                    'user', 'user__userrole' 
                ).get(user_id=user_id)
                if user_profile.user.userrole.role != 'student':
                    return JsonResponse({"detail": "User is not a student."}, status=status.HTTP_400_BAD_REQUEST)
                serializer = StudentProfileSerializer(user_profile)
                return JsonResponse(serializer.data)
            else:
                profiles = StudentProfile.objects.select_related(
                    'user', 'user__userrole' 
                )
                student_profiles = [profile for profile in profiles if profile.user.userrole.role == 'student']
                serializer = StudentProfileSerializer(student_profiles, many=True)
                return JsonResponse(serializer.data)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return JsonResponse({"detail": "User or Role not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        try:
            student_id = request.data.get('student_id')  # Expecting student_id in payload
            if student_id:
                try:
                    user = User.objects.get(id=student_id)
                    user_role = UserRole.objects.get(user=user)
                    if user_role.role != 'student':
                        return JsonResponse({"detail": "Provided user is not a student."}, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return JsonResponse({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                except UserRole.DoesNotExist:
                    return JsonResponse({"detail": "User does not have a role."}, status=status.HTTP_400_BAD_REQUEST)
                profile, created = StudentProfile.objects.get_or_create(user=user)
            else:
                return JsonResponse({"detail": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = StudentProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                if created:
                    return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)  
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request, user_id=None):
        try:
            if not user_id:
                return JsonResponse({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            profile = get_object_or_404(StudentProfile.objects.select_related('user', 'user__userrole'), user_id=user_id)
            if profile.user.userrole.role != 'student':
                return JsonResponse({"detail": "User is not a student."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = StudentProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return JsonResponse({"detail": "User or Role not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request, user_id=None):
        try:
            if not user_id:
                return JsonResponse({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            profile = get_object_or_404(StudentProfile.objects.select_related('user', 'user__userrole'), user_id=user_id)
            # Check if the user is a student
            if profile.user.userrole.role != 'student':
                return JsonResponse({"detail": "User is not a student."}, status=status.HTTP_400_BAD_REQUEST)
            profile.delete()
            return JsonResponse(status=status.HTTP_204_NO_CONTENT)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return JsonResponse({"detail": "User or Role not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ================ student profile image =================
class ProfilePictureUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        profile_picture = request.FILES.get('profile_picture')
        if not student_id or not profile_picture:
            return JsonResponse({"error": "Student ID and profile picture are required."}, status=400)
        try:
            student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=404)
        try:
            profile = StudentProfile.objects.get(user=student)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"error": "Student profile not found."}, status=404)
        student_name = f"{profile.first_name}_{profile.last_name}"
        student_name_slug = slugify(student_name).replace(" ", "_")
        ext = os.path.splitext(profile_picture.name)[-1].lower()
        new_filename = f"{student_name_slug}_{uuid.uuid4().hex[:8]}{ext}"
        file_key = f"student_profiles/{new_filename}"
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        try:
            s3.upload_fileobj(
                profile_picture,
                settings.AWS_STORAGE_BUCKET_NAME,
                file_key,
                ExtraArgs={'ACL': 'public-read', 'ContentType': profile_picture.content_type}
            )
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
            profile.profile_picture = file_url
            profile.save()
            return JsonResponse({
                "student_id": student.id,
                "profile_picture_url": file_url
            }, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=500)


