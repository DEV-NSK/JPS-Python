from django.contrib import admin
from .models import (
    CodingProblem, CodingSubmission, UserXP, MockInterviewSession,
    LearningPath, PeerRoom, ReputationScore, InterviewRoom,
    Project, ProjectSubmission, ResumeMatch, ReadinessScore,
)


@admin.register(CodingProblem)
class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'topic', 'xp', 'is_active']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['title', 'topic']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(CodingSubmission)
class CodingSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'status', 'xp_earned', 'created_at']
    list_filter = ['status', 'language']


@admin.register(UserXP)
class UserXPAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_xp', 'today_xp', 'last_reset_date']


@admin.register(MockInterviewSession)
class MockInterviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'mode', 'role', 'overall_score', 'status', 'created_at']


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_role', 'total_days', 'is_fast_track']


@admin.register(ReputationScore)
class ReputationAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score', 'tier', 'percentile']


admin.site.register(InterviewRoom)
admin.site.register(Project)
admin.site.register(ProjectSubmission)
admin.site.register(ResumeMatch)
admin.site.register(ReadinessScore)
admin.site.register(PeerRoom)
