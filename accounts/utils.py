import random
import hashlib
from django.utils import timezone

def generate_and_send_otp(user, request):
    otp = str(random.randint(100000, 999999))
    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

    user.otp = hashed_otp
    user.otp_created_at = timezone.now()

    ip = request.META.get('REMOTE_ADDR')
    if not user.register_ip:
        user.register_ip = ip
    user.save()

    # Replace with actual email sending
    print(f"[DEBUG] Sending OTP {otp} to {user.email}")

