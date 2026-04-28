from django.db import models
from django.conf import settings


class RecruiterPin(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pins')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE)
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pinned_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recruiter_pins'
        unique_together = ('recruiter', 'job', 'candidate')


class ShortlistAudit(models.Model):
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE)
    candidates = models.JSONField(default=list)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shortlist_audits'


class CandidateTimeline(models.Model):
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='timeline')
    event_type = models.CharField(max_length=50)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    actor_role = models.CharField(max_length=20, default='recruiter')
    details = models.JSONField(default=dict)
    note = models.TextField(blank=True, default='')
    is_recruiter_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'candidate_timelines'
        ordering = ['created_at']


class BlindHiringReveal(models.Model):
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE)
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    revealed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blind_hiring_reveals'


class TalentPool(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='talent_pools')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    is_team_visible = models.BooleanField(default=False)
    members = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'talent_pools'
