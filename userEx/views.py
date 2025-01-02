import json
from django.http import HttpResponse
from django.shortcuts import render
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


#============ Views ====================
class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "user_id": user.id,
                "message": "User registered successfully.",
                "username": user.username,
                "token": token.key,
                "role": serializer.validated_data['role'],
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ========= user Login ===========
class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_role = UserRole.objects.get(user=user).role
            token, created = Token.objects.get_or_create(user=user)
            full_name = f"{user.first_name} {user.last_name}"
            return Response({
                "message": "Login successful.",
                "user_id": user.id,
                "full_name": full_name,
                "token": token.key,
                "role": user_role 
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# =================== User reset password =================
class ForgetPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error" : "User with this email not found."}, status=status.HTTP_404_NOT_FOUND)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        frontend_reset_url = f"https://inpath.us/resetpassword/{uid}/{token}"
        try:
            send_mail(
                subject="Reset your password",
                message=f"Click the link to reset your password: {frontend_reset_url}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "Reset link sent to your email."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ========== Reset password ================
import base64
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid = data.get('uid')
            token = data.get('token')
            new_password = data.get('new_password')
            if not uid or not token or not new_password:
                return HttpResponse("Invalid reset link or missing data", status=400)
            try:
                padding = '=' * (4 - (len(uid) % 4))
                uid_with_padding = uid + padding
                decoded_uid = base64.urlsafe_b64decode(uid_with_padding).decode('utf-8')  # Decode and convert to string
                user_id = int(decoded_uid)
            except (ValueError, TypeError, base64.binascii.Error):
                return HttpResponse("Invalid UID format", status=400)
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponse("Invalid user", status=400)
            if not validate_token(user, token):
                return HttpResponse("Invalid or expired token", status=400)
            user.set_password(new_password)
            user.save()
            return HttpResponse("Password reset successfully. Please log in.", status=200)
        except json.JSONDecodeError:
            return HttpResponse("Invalid JSON format", status=400)
    else:
        return HttpResponse("Invalid request method", status=405)
def validate_token(user, token):
    return default_token_generator.check_token(user, token)
