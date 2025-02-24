from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Extend fieldsets if you want to include your extra fields
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('address', 'store_name', 'phone_number', 'image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('address', 'store_name', 'phone_number', 'image')}),
    )
