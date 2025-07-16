from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_verified', 'register_country', 'verified_country', 'date_joined')
    list_filter = ('is_verified', 'register_country', 'verified_country')
    readonly_fields = ('date_joined', 'register_ip', 'register_country', 'verified_ip', 'verified_country')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Verification', {'fields': ('is_verified', 'otp_created_at')}),
        ('Geo Info', {'fields': (
            'register_ip', 'register_country', 'register_region', 'register_city', 'register_isp',
            'verified_ip', 'verified_country', 'verified_region', 'verified_city', 'verified_isp',
            'user_agent'
        )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
