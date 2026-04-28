from django.contrib import admin
from .models import Job, Bookmark


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'type', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'tier']
    search_fields = ['title', 'company_name', 'location']
    ordering = ['-created_at']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
