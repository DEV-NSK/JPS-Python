from django.db import models
from django.conf import settings


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'),
    ]
    FUNNEL_STAGES = [
        ('applied', 'Applied'), ('screened', 'Screened'), ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'), ('interview_done', 'Interview Done'),
        ('offer_extended', 'Offer Extended'), ('selected', 'Selected'), ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, default='')
    resume = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    funnel_stage = models.CharField(max_length=30, choices=FUNNEL_STAGES, default='applied')
    funnel_stage_entered_at = models.DateTimeField(auto_now_add=True)
    stage_history = models.JSONField(default=list, blank=True)
    ranking_score = models.FloatField(default=0)
    is_shortlisted = models.BooleanField(default=False)
    is_vetoed = models.BooleanField(default=False)
    recruiter_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'applications'
        unique_together = ('job', 'applicant')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.applicant.name} → {self.job.title}'
