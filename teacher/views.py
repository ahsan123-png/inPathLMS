from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
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
    def get(self, request, pk=None):
        if pk:
            try:
                profile = InstructorProfile.objects.get(pk=pk)
                serializer = InstructorProfileSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except InstructorProfile.DoesNotExist:
                return Response({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            profiles = InstructorProfile.objects.all()
            serializer = InstructorProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = InstructorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, pk):
        try:
            profile = InstructorProfile.objects.get(pk=pk)
            serializer = InstructorProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except InstructorProfile.DoesNotExist:
            return Response({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk):
        try:
            profile = InstructorProfile.objects.get(pk=pk)
            profile.delete()
            return Response({"message": "Instructor profile deleted."}, status=status.HTTP_204_NO_CONTENT)
        except InstructorProfile.DoesNotExist:
            return Response({"error": "Instructor not found."}, status=status.HTTP_404_NOT_FOUND)
