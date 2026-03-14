from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'pseudo', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'pseudo']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations', {'fields': ('pseudo', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'pseudo', 'password1', 'password2'),
        }),
    )