import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
import requests
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from google_auth_oauthlib.flow import Flow
#============ Views ====================
class SignupAPIView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            if send_welcome_email(user):
                email_message = "Welcome email sent successfully."
            else:
                email_message = "Failed to send welcome email."
            return Response({
                "user_id": user.id,
                "message": "User registered successfully.",
                "username": user.username,
                "token": token.key,
                "role": serializer.validated_data['role'],
                "email_message": email_message
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
# ========================== Welcoming Mail ==============================
def send_welcome_email(user):
    subject = f"Welcome to Our Platform, {user.first_name}!"
    signup_date = user.date_joined.strftime("%B %d, %Y")
    message = f"""
    Hello {user.first_name},

    Welcome to our platform! We're absolutely thrilled to have you join our community. 🌟

    Your journey with us started on {signup_date}, and we can't wait to be part of your learning and growth. 
    Whether you're here to explore courses, engage with instructors, or connect with fellow students, we're here to support you every step of the way.

    If you ever need help or have any questions, feel free to reach out to us anytime. We're always here for you.

    Best regards,
    The InPath Team

    P.S. We hope you have a fantastic experience with us and enjoy all the amazing opportunities ahead!
    """
    
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True
# ===================== Initiate Google OAuth Flow =================
@csrf_exempt
def google_login(request):
    role = request.GET.get('role')
    if not role or role not in ['student', 'instructor', 'admin']:
        return JsonResponse({'error': 'Invalid or missing role'}, status=400)
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_JSON,
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ],
        redirect_uri="https://api.inpath.us/users/google/callback/"
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    request.session['user_role'] = role
    return HttpResponseRedirect(authorization_url)
# ====================== Handle Google Callback =================
@csrf_exempt
def google_callback(request):
    state = request.session.get('oauth_state')
    code = request.GET.get('code')
    role = request.session.get('user_role')  # Retrieve the role from the session
    if not code:
        return JsonResponse({'error': 'Authorization code not provided', 'state': state, 'role': role}, status=400)
    if not role or role not in ['student', 'instructor', 'admin']:
        return JsonResponse({'error': 'Invalid or missing role', 'state': state, 'role': role}, status=400)
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_JSON,
        scopes=[
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ],
        redirect_uri="https://api.inpath.us/users/google/callback/"
    )
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        access_token = credentials.token
        user_info_url = 'https://openidconnect.googleapis.com/v1/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        if user_info_response.status_code == 200:
            user_info = user_info_response.json()
            email = user_info.get('email')
            first_name = user_info.get('given_name')
            last_name = user_info.get('family_name')
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            if created:
                UserRole.objects.create(user=user, role=role)
            return JsonResponse({
                'user_info': user_info,
                'created': created,
                'role': role,
                'state': state
            })
        else:
            return JsonResponse({'error': 'Failed to fetch user info', 'state': state, 'role': role}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e), 'state': state, 'role': role}, status=500)


