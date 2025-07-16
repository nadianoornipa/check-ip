from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=128, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    register_ip = models.GenericIPAddressField(blank=True, null=True)
    register_country = models.CharField(max_length=100, blank=True, null=True)
    register_region = models.CharField(max_length=100, blank=True, null=True)
    register_city = models.CharField(max_length=100, blank=True, null=True)
    register_isp = models.CharField(max_length=255, blank=True, null=True)

    verified_ip = models.GenericIPAddressField(blank=True, null=True)
    verified_country = models.CharField(max_length=100, blank=True, null=True)
    verified_region = models.CharField(max_length=100, blank=True, null=True)
    verified_city = models.CharField(max_length=100, blank=True, null=True)
    verified_isp = models.CharField(max_length=255, blank=True, null=True)

    user_agent = models.TextField(blank=True, null=True)

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
