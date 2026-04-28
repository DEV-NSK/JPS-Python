from django.db import models
from django.conf import settings


class Job(models.Model):
    TYPE_CHOICES = [
        ('Full-time', 'Full-time'), ('Part-time', 'Part-time'),
        ('Remote', 'Remote'), ('Contract', 'Contract'), ('Internship', 'Internship'),
    ]
    TIER_CHOICES = [('promoted', 'Promoted'), ('standard', 'Standard'), ('high', 'High')]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    company_name = models.CharField(max_length=255)
    company_logo = models.CharField(max_length=500, blank=True, default='')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.JSONField(default=list, blank=True)
    location = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Full-time')
    salary = models.CharField(max_length=100, blank=True, default='')
    experience = models.CharField(max_length=100, blank=True, default='')
    skills = models.JSONField(default=list, blank=True)
    category = models.CharField(max_length=100, blank=True, default='')
    deadline = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    applicants_count = models.IntegerField(default=0)
    # Blind Hiring
    blind_mode = models.BooleanField(default=False)
    blind_mode_locked = models.BooleanField(default=False)
    # Skill-Based Posting
    required_skills = models.JSONField(default=list, blank=True)
    is_skill_based = models.BooleanField(default=False)
    min_match_threshold = models.IntegerField(default=70)
    # Dynamic Job Health
    health_score = models.IntegerField(default=50)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='standard')
    is_urgent = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)
    tier_locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company_name}'


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bookmarks'
        unique_together = ('user', 'job')
