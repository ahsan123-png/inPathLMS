from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.http import JsonResponse
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

