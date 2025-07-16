from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
import random
import requests
from django.contrib.auth.hashers import make_password

from .models import CustomUser
from .serializers import RegisterSerializer, OTPVerificationSerializer

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

def get_geo_info(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country_name"),
                "region": data.get("region"),
                "city": data.get("city"),
                "isp": data.get("org")
            }
    except:
        pass
    return {}

def generate_and_send_otp(user):
    raw_otp = str(random.randint(100000, 999999))
    user.otp = make_password(raw_otp)
    user.otp_created_at = timezone.now()
    user.save()

    send_mail(
        subject='Your OTP Code',
        message=f'Your OTP is: {raw_otp}',
        from_email='nadianipa002@gmail.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp_created_at and timezone.now() - user.otp_created_at > timedelta(seconds=60):
            return Response({'error': 'OTP expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        if check_password(otp, user.otp):
            ip = get_client_ip(request)
            geo = get_geo_info(ip)

            user.verified_ip = ip
            user.verified_country = geo.get("country")
            user.verified_region = geo.get("region")
            user.verified_city = geo.get("city")
            user.verified_isp = geo.get("isp")
            user.user_agent = request.META.get('HTTP_USER_AGENT', '')
            user.is_verified = True
            user.otp = ''
            user.save()

            return Response({'message': 'OTP is correct — Registration successful!'}, status=status.HTTP_200_OK)

        return Response({'message': 'Invalid OTP — Registration unsuccessful.'}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"message": "User already verified."}, status=status.HTTP_400_BAD_REQUEST)

        generate_and_send_otp(user)
        return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)
