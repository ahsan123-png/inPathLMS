from dotenv import load_dotenv
import os
from pathlib import Path
import boto3
import json
from django.core.exceptions import ImproperlyConfigured
from botocore.exceptions import ClientError
#=========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-87!g1cj*9i-s5l-_$0s+sgz%rw8$5x350g#*p4*n0f2#)^ihdh'
DEBUG = True
load_dotenv() 
ALLOWED_HOSTS = ['*']
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'allauth',
    'rest_auth',
    'userEx',
    'student',
    'teacher',
    'category',
    'payments',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'inpath_lms.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'inpath_lms.wsgi.application'
# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
#==================++++++++++++++++++++ Get secrets with Boto3 ++++++++++++++++++++++++++======================
def get_secret(secret_name, region_name="eu-north-1"):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise ImproperlyConfigured(f"Error retrieving secret {secret_name}: {e}")
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)
# ==================++++++++++++++++++++ accessibility with Boto3 ++++++++++++++++++++++++++======================
secret_name = "viseLMS" 
secrets = get_secret(secret_name)
DB_USER = secrets.get('DB_USER')
DB_PASSWORD = secrets.get('DB_PASSWORD')
DB_HOST = secrets.get('DB_HOST')
DB_NAME = secrets.get('DB_NAME')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '3306',
    }
}

#============= AWS S3 Bucket Secrets ===========================
# Fetch S3 credentials from Secrets Manager
secret_name = "lms/bukets"  # Use the secret name you've stored for your S3 credentials
buketsSecrets = get_secret(secret_name)
AWS_STORAGE_BUCKET_NAME = buketsSecrets.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = buketsSecrets.get('AWS_S3_REGION_NAME')
AWS_ACCESS_KEY_ID = buketsSecrets.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = buketsSecrets.get('AWS_SECRET_ACCESS_KEY')
# Optional: Set up a custom domain for your S3 bucket
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
AWS_S3_SIGNATURE_VERSION = 's3v4'  # Use version 4 signing (default)
if DEBUG:  # Local Development
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:  # Production (AWS S3)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# Assign S3 credentials to settings
AWS_S3_CUSTOM_DOMAIN = AWS_S3_CUSTOM_DOMAIN
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME = AWS_S3_REGION_NAME

# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME') # Example: 'us-east-1'
# AWS_S3_SIGNATURE_VERSION = 's3v4'
# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# ====================== Database Configs ===========================================
# DB_NAME = os.getenv('NAME')
# DB_USER = os.getenv('USER')
# DB_PASSWORD = os.getenv('PASSWORD')
# DB_HOST = os.getenv('HOST')
# DB_PORT = os.getenv('PORT', '3306')
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': '3306',  # Default MySQL port
#     }
# }
# ======================================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = 'static/'
MEDIA_URL =f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# REST_FRAMEWORK = {
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.SessionAuthentication',
#         'rest_framework.authentication.TokenAuthentication',
#     ],
# }
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',  # Local development
#     'https://inpath.us',      # Production frontend
# ]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
    'x-requested-with',
    'accept',
    'origin',
    'x-csrftoken',
]
CORS_ALLOW_CREDENTIALS = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600 
FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600
STRIPE_PUBLIC_KEY="pk_test_51Pw4qzEnQNLsnCj14FKz4CjTGplHuZb9a72NWOEwOmhpfiHZ57RckjlZZusgcJYBk9OIDfvlUTtioU3pkFbTEdXt0075iT2P8j"
STRIPE_SECRET_KEY="sk_test_51Pw4qzEnQNLsnCj1NLNJftCJaYhNo7ZYB2YntOJsO4OlQsscEdmZSCTRPlqBnnkFTKbs94g0bWQMXBsnizBzXdhh00lvuKtAqu"