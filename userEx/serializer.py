from django.contrib.auth.models import User
from rest_framework import serializers
from userEx.models import UserRole
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import re

class SignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'role']
    def validate(self, data):
        # Ensure all required fields are provided
        if 'full_name' not in data or 'email' not in data or 'password' not in data or 'role' not in data:
            raise serializers.ValidationError("All fields (full_name, email, password, role) are required.")
        if data['role'] not in ['admin', 'instructor', 'student']:
            raise serializers.ValidationError("Invalid role. Role must be 'admin', 'instructor', or 'student'.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already taken. Please try another.")
        return data
    def create(self, validated_data):
        full_name = validated_data['full_name']
        email = validated_data['email']
        password = validated_data['password']
        role = validated_data['role']
        first_name = full_name.split()[0]
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        username_part = email.split('@')[0]
        username = f"{username_part}_{len(email)}"  
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserRole.objects.create(user=user, role=role)
        return user
#============== Login Serializer ==============
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            try:
                # Attempt to retrieve the user using the email
                user = User.objects.get(email=email)
                # Authenticate with username and password
                user = authenticate(username=user.username, password=password)  # Use the username retrieved from email
                if user is None:
                    raise serializers.ValidationError("Invalid email or password.")
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")
            data['user'] = user
        else:
            raise serializers.ValidationError("Both 'email' and 'password' are required.")   
        return data
    
