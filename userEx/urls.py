from django.contrib import admin
from django.urls import path,include
from .views import *
#======== urls ==========
urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
]