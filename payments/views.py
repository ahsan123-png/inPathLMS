import json
from django.http import JsonResponse
from django.shortcuts import render
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from userEx.models import *
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
# ================= payments views =================
class CreatePaymentIntentView(APIView):
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            data=json.loads(request.body)
            user_id = data.get('user')
            user = User.objects.get(id=user_id)
            user_role = UserRole.objects.filter(user=user).first()
            if not user_role or user_role.role != 'student':
                return JsonResponse({"detail": "Only students can purchase courses."}, status=403)
            final_price = course.get_discounted_price()
            payment_intent = stripe.PaymentIntent.create(
                amount=int(final_price * 100),
                currency="usd",
                metadata={
                    "course_id": course.id,
                    "user_id": user
                },
            )
            enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
            Payment.objects.create(
                enrollment=enrollment,
                amount=final_price,
                payment_status='pending'
            )
            return JsonResponse(
                {"client_secret": payment_intent["client_secret"]},
                status=200
            )
        except Course.DoesNotExist:
            return JsonResponse({"detail": "Course not found."}, status=404)
        except stripe.error.StripeError as e:
            return JsonResponse({"detail": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=500)
# ================= Confirmation +========================
class ConfirmPaymentView(APIView):
    def post(self, request):
        payment_intent_id = request.data.get("payment_intent_id")
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent["status"] == "succeeded":
                payment = Payment.objects.get(stripe_payment_intent=payment_intent_id)
                payment.is_successful = True
                payment.save()
                return Response({"detail": "Payment successful. Course access granted."}, status=status.HTTP_200_OK)
            return Response({"detail": "Payment not successful yet."}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
