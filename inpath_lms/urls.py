from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
#======== urls ==========
urlpatterns = [
    path('admin/', admin.site.urls),
    path('teacher/', include('teacher.urls')),
    path('students/', include('student.urls')),
    path('users/', include('userEx.urls')),
    path('courses/', include('category.urls')),
    path('payments/', include('payments.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)