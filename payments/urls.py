from django.urls import path
from .views import *
urlpatterns = [
    path('create/<int:course_id>/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('payments/confirm/', ConfirmPaymentView.as_view(), name='confirm_payment'),
]
