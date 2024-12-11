from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
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