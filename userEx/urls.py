from django.contrib import admin
from django.urls import path,include
from .views import *
#======== urls ==========
urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgot-password/', ForgetPasswordAPIView.as_view(), name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('google/login/', google_login, name='google_login'),  # URL to initiate the login process
    path('google/callback/',google_callback, name='google_callback')
]