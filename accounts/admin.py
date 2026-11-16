from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('TeknoyHelp', {'fields': ('role', 'contact_number', 'profile_photo')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('TeknoyHelp', {'fields': ('email', 'role', 'contact_number')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')