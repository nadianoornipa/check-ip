from rest_framework import serializers
from .models import CustomUser
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import random
import requests

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        request = self.context.get('request')
        user = CustomUser.objects.create_user(**validated_data)

        # OTP generation
        raw_otp = str(random.randint(100000, 999999))
        user.otp = make_password(raw_otp)
        user.otp_created_at = timezone.now()

        # Get IP and geo info
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
            user.register_ip = ip

            try:
                res = requests.get(f"https://ipapi.co/{ip}/json/")
                if res.status_code == 200:
                    data = res.json()
                    user.register_country = data.get("country_name")
                    user.register_region = data.get("region")
                    user.register_city = data.get("city")
                    user.register_isp = data.get("org")
            except Exception as e:
                # Optional: log or debug print(e)
                pass

        user.save()

        # Send OTP email
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is: {raw_otp}',
            from_email='nadianipa002@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user
