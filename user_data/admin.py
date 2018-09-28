from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'profile_avatar',
        'sur_name',
        'mobile',
        'mobile_verified',
        'address',
        'user'
    )
