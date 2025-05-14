from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FieldManager

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active', 'role')
    search_fields = ('email',)
    ordering = ('email',)  # Fix: Change 'username' to 'email'

    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(FieldManager)
