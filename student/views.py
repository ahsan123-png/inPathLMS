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
class StudentDetailsViews(APIView):
    def get(self, request, user_id=None):
        """
        GET all students or a specific student by `user_id`.
        """
        if user_id is None:
            # Fetch all students with their profiles
            users = User.objects.filter(userrole__role='student')  # Ensure only students are fetched
            serializer = StudentDetailsSerializer(users, many=True)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

        # Fetch a single student by user_id
        user = get_object_or_404(User, id=user_id, userrole__role='student')
        serializer = StudentDetailsSerializer(user)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        """
        Update a student's details and profile by `user_id`.
        """
        user = get_object_or_404(User, id=user_id, userrole__role='student')
        profile = get_object_or_404(StudentProfile, user=user)

        # Serialize user data
        user_serializer = StudentDetailsSerializer(user, data=request.data, partial=True)
        # Serialize profile data (if provided)
        profile_serializer = StudentProfileSerializer(profile, data=request.data.get('profile', {}), partial=True)

        if user_serializer.is_valid() and profile_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            return JsonResponse({
                "user": user_serializer.data,
                "profile": profile_serializer.data
            }, status=status.HTTP_200_OK)

        errors = {
            "user_errors": user_serializer.errors,
            "profile_errors": profile_serializer.errors
        }
        return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)
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
            user_id = request.data.get('user_id')  # Expecting student_id in payload
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
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
        user_id = request.data.get('user_id')
        profile_picture = request.FILES.get('profile_picture')
        if not user_id or not profile_picture:
            return JsonResponse({"error": "User ID and profile picture are required."}, status=400)
        try:
            student = User.objects.select_related('studentprofile').get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        try:
            profile = student.studentprofile
        except StudentProfile.DoesNotExist:
            return JsonResponse({"error": "Student profile not found."}, status=404)
        student_name = f"{profile.first_name}_{profile.last_name}"
        student_name_slug = slugify(student_name).replace(" ", "_")
        ext = os.path.splitext(profile_picture.name)[-1].lower()
        new_filename = f"{student_name_slug}_{uuid.uuid4().hex[:8]}{ext}"
        file_key = f"student_profiles/{new_filename}"
        try:
            file_url = upload_to_s3(profile_picture, file_key)
            if profile.profile_picture:
                profile.profile_picture = file_url
            else:
                profile.profile_picture = file_url
            profile.save()
            return JsonResponse({
                "user_id": student.id,
                "profile_picture_url": file_url
            }, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
# ========================== upload_file =========================
def upload_to_s3(file, file_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    try:
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_key,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
        )
        file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"
        return file_url
    except Exception as e:
        raise Exception(f"Failed to upload image: {str(e)}")
# Refactored ProfilePictureUploadView

