import boto3
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import *
from userEx.models import *
# ============== CBV CURD =============== 

class StudentProfileView(APIView):
    def get_user_role(self, user):
        try:
            return UserRole.objects.select_related('user').get(user=user)
        except UserRole.DoesNotExist:
            return None
    def get(self, request, pk=None):
        if pk:
            try:
                user = User.objects.select_related('userrole').get(pk=pk)
                user_role = self.get_user_role(user)
                if user_role is None or user_role.role != 'student':
                    return JsonResponse(
                        {"error": "The provided user ID does not belong to a student. Please provide a valid Student ID."},status=status.HTTP_400_BAD_REQUEST
                    )
                # student_details =User.objects.filter(userrole__role='student').prefetch_related('userrole')
                serializer = StudentProfileSerializer(user)
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            except User.DoesNotExist:
                return JsonResponse({"error": "Student details not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            students = User.objects.select_related('userrole').filter(userrole__role='student')
            serializer = StudentProfileSerializer(students, many=True)
            return JsonResponse(serializer.data,safe=False, status=status.HTTP_200_OK)
    def put(self, request, pk):
        try:
            user = User.objects.select_related('userrole').get(pk=pk)
            user_role = self.get_user_role(user)
            if user_role is None or user_role.role != 'student':
                return JsonResponse(
                    {"error": "The provided user ID does not belong to a student. Please provide a valid Student ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            old_password = request.data.get('old_password')
            new_password = request.data.get('password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            # Verify old password
            if old_password and not check_password(old_password, user.password):
                return JsonResponse(
                    {"error": "The provided old password is incorrect. Please provide the correct password."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if new_password:
                user.set_password(new_password)  # Hash the new password
                update_session_auth_hash(request, user)  # Keep the user logged in after password change
            user.save()  # Save the user object
            serializer = StudentProfileSerializer(user)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        try:
            user = User.objects.select_related('userrole').get(pk=pk)
            user_role = self.get_user_role(user)
            if user_role is None or user_role.role != 'student':
                return JsonResponse(
                    {"error": "The provided user ID does not belong to a student. Please provide a valid Student ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.delete()  # Directly delete the user instance
            return JsonResponse({"message": "Student profile deleted."}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return JsonResponse({"error": "Student details not found."}, status=status.HTTP_404_NOT_FOUND)


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
from rest_framework import status
from rest_framework.response import Response
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
from rest_framework.response import Response
from rest_framework import status
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
    def get(self, request, pk=None):
        try:
            if pk:
                profile = StudentProfile.objects.get(pk=pk)
                serializer = StudentProfileSerializer(profile)
                return Response(serializer.data)
            else:
                profiles = StudentProfile.objects.all()
                serializer = StudentProfileSerializer(profiles, many=True)
                return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def post(self, request):
        try:
            student_id = request.data.get('student_id')  # Expecting student_id in payload
            if student_id:
                try:
                    user = User.objects.get(id=student_id)
                    user_role = UserRole.objects.get(user=user)
                    if user_role.role != 'student':
                        return Response({"detail": "Provided user is not a student."}, status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                except UserRole.DoesNotExist:
                    return Response({"detail": "User does not have a role."}, status=status.HTTP_400_BAD_REQUEST)
                profile, created = StudentProfile.objects.get_or_create(user=user)
            else:
                return Response({"detail": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = StudentProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                if created:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.data, status=status.HTTP_200_OK)  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def put(self, request, pk=None):
        try:
            profile = StudentProfile.objects.get(pk=pk)
            serializer = StudentProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def delete(self, request, pk=None):
        try:
            profile = StudentProfile.objects.get(pk=pk)
            profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ================ student profile image =================
class ProfilePictureUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        profile_picture = request.FILES.get('profile_picture')
        if not student_id or not profile_picture:
            return JsonResponse({"error": "Student ID and profile picture are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = User.objects.get(id=student_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            profile = StudentProfile.objects.get(user=student)
        except StudentProfile.DoesNotExist:
            return JsonResponse({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        file_name = os.path.basename(profile_picture.name)
        file_key = f"student_profiles/{file_name}"
        try:
            s3.upload_fileobj(
                profile_picture,
                settings.AWS_STORAGE_BUCKET_NAME,
                f"media/{file_key}",
                ExtraArgs={'ACL': 'public-read', 'ContentType': profile_picture.content_type}
            )
            file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/media/{file_key}"
            profile.profile_picture = file_url
            profile.save()
            return JsonResponse({
                "student_id": student.id,
                "profile_picture_url": file_url
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": f"Failed to upload image: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

