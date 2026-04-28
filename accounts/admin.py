from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Employer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'role', 'approval_status', 'is_active', 'created_at']
    list_filter = ['role', 'approval_status', 'is_active']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'bio', 'location', 'phone', 'avatar', 'resume')}),
        ('Professional', {'fields': ('skills', 'experience', 'education', 'linkedin', 'github')}),
        ('Permissions', {'fields': ('role', 'is_approved', 'approval_status', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'name', 'password1', 'password2', 'role')}),
    )


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'industry', 'location']
    search_fields = ['company_name', 'user__email']
