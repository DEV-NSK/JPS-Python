from django.db import models
from django.conf import settings


class MicroInternship(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('closed', 'Closed'), ('draft', 'Draft')]

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='micro_internships')
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.JSONField(default=list)
    duration_days = models.IntegerField(default=3)
    compensation = models.CharField(max_length=100, blank=True, default='')
    max_candidates = models.IntegerField(default=5)
    deliverable = models.TextField(blank=True, default='')
    rubric = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    applicants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='internship_applications', blank=True
    )
    accepted = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='internship_accepted', blank=True
    )
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'micro_internships'
        ordering = ['-created_at']


class MicroInternshipSubmission(models.Model):
    EVAL_CHOICES = [('excellent', 'Excellent'), ('good', 'Good'), ('below_expectation', 'Below Expectation')]

    internship = models.ForeignKey(MicroInternship, on_delete=models.CASCADE, related_name='submissions')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='internship_submissions')
    deliverable_text = models.TextField(blank=True, default='')
    deliverable_url = models.CharField(max_length=500, blank=True, default='')
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    evaluation = models.CharField(max_length=30, choices=EVAL_CHOICES, default='good')
    recruiter_notes = models.TextField(blank=True, default='')
    fast_tracked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'micro_internship_submissions'
        unique_together = ('internship', 'candidate')
