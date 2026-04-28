from django.db import models
from django.conf import settings


# ── F1: AI Career Copilot ─────────────────────────────────────────────────────
class CopilotGoal(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='copilot_goal')
    target_role = models.CharField(max_length=255, default='Software Engineer')
    timeline = models.CharField(max_length=100, default='3 months')
    company_tier = models.CharField(max_length=100, default='Any')
    target_company = models.CharField(max_length=255, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'copilot_goals'


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    text = models.TextField()
    rating = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']


class ReadinessScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='readiness_scores')
    score = models.IntegerField(default=0)
    dimensions = models.JSONField(default=list)
    badge = models.CharField(max_length=20, default='Bronze')
    percentile = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'readiness_scores'
        ordering = ['-created_at']


# ── F4: Resume Match ──────────────────────────────────────────────────────────
class ResumeMatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_matches')
    job_title = models.CharField(max_length=255, blank=True, default='')
    job_description = models.TextField(blank=True, default='')
    job_url = models.CharField(max_length=500, blank=True, default='')
    match_score = models.IntegerField(default=0)
    ats_probability = models.IntegerField(default=0)
    domain_overlap = models.IntegerField(default=0)
    hard_skills_missing = models.JSONField(default=list)
    soft_skills_missing = models.JSONField(default=list)
    experience_delta = models.CharField(max_length=255, blank=True, default='')
    keyword_matches = models.JSONField(default=list)
    keyword_missing = models.JSONField(default=list)
    resume_suggestions = models.JSONField(default=list)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resume_matches'
        ordering = ['-created_at']


# ── F5: Consistency Tracker ───────────────────────────────────────────────────
class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')
    activity = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'activity_logs'


class UserStreak(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    daily_goal = models.IntegerField(default=1)

    class Meta:
        db_table = 'user_streaks'


# ── F6: Daily Coding Practice ─────────────────────────────────────────────────
class CodingProblem(models.Model):
    DIFFICULTY_CHOICES = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    topic = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField()
    examples = models.JSONField(default=list)
    constraints = models.JSONField(default=list)
    starter_code = models.JSONField(default=dict)
    test_cases = models.JSONField(default=list)
    optimal_solution = models.TextField(blank=True, default='')
    time_complexity = models.CharField(max_length=50, blank=True, default='')
    space_complexity = models.CharField(max_length=50, blank=True, default='')
    xp = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coding_problems'


class CodingSubmission(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'), ('wrong_answer', 'Wrong Answer'),
        ('time_limit', 'Time Limit'), ('error', 'Error'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coding_submissions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wrong_answer')
    runtime = models.CharField(max_length=50, blank=True, default='')
    memory = models.CharField(max_length=50, blank=True, default='')
    xp_earned = models.IntegerField(default=0)
    test_results = models.JSONField(default=list)
    quality_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coding_submissions'
        ordering = ['-created_at']


class UserXP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp')
    total_xp = models.IntegerField(default=0)
    today_xp = models.IntegerField(default=0)
    last_reset_date = models.CharField(max_length=10, default='')
    log = models.JSONField(default=list)

    class Meta:
        db_table = 'user_xp'


# ── F7: Interview Rooms ───────────────────────────────────────────────────────
class InterviewRoom(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'), ('active', 'Active'),
        ('completed', 'Completed'), ('cancelled', 'Cancelled'),
    ]

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_rooms')
    title = models.CharField(max_length=255)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    invitee_email = models.EmailField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    recording_url = models.CharField(max_length=500, blank=True, default='')
    recording_consent = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)
    post_session_report = models.JSONField(default=dict, blank=True)
    chat_log = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interview_rooms'
        ordering = ['-created_at']


# ── F8: Code Quality ──────────────────────────────────────────────────────────
class CodeQualityResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='code_quality_results')
    code = models.TextField()
    language = models.CharField(max_length=50)
    overall_score = models.IntegerField(default=0)
    readability = models.IntegerField(default=0)
    maintainability = models.IntegerField(default=0)
    performance = models.IntegerField(default=0)
    security = models.IntegerField(default=0)
    issues = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'code_quality_results'
        ordering = ['-created_at']


# ── F9: Project-Based Hiring ──────────────────────────────────────────────────
class Project(models.Model):
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, default='')
    company_logo = models.CharField(max_length=500, blank=True, default='')
    domain = models.CharField(max_length=100, blank=True, default='')
    difficulty = models.CharField(max_length=20, default='Medium')
    duration_hours = models.IntegerField(default=4)
    reward = models.CharField(max_length=100, blank=True, default='')
    tech_stack = models.JSONField(default=list)
    description = models.TextField()
    requirements = models.JSONField(default=list)
    starter_code_url = models.CharField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)
    submissions_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']


class ProjectSubmission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_submissions')
    code = models.TextField(blank=True, default='')
    repo_url = models.CharField(max_length=500, blank=True, default='')
    score = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_submissions'


# ── F10: Mock Interview ───────────────────────────────────────────────────────
class MockInterviewSession(models.Model):
    MODE_CHOICES = [('hr', 'HR'), ('technical', 'Technical')]
    STATUS_CHOICES = [('active', 'Active'), ('completed', 'Completed')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mock_interviews')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    role = models.CharField(max_length=100)
    input_mode = models.CharField(max_length=20, default='text')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    questions = models.JSONField(default=list)
    overall_score = models.FloatField(default=0)
    report = models.JSONField(default=dict, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mock_interview_sessions'
        ordering = ['-created_at']


# ── F11: Learning Path ────────────────────────────────────────────────────────
class LearningPath(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_path')
    target_role = models.CharField(max_length=255)
    total_days = models.IntegerField(default=60)
    current_day = models.IntegerField(default=1)
    estimated_ready_date = models.CharField(max_length=100, blank=True, default='')
    is_fast_track = models.BooleanField(default=False)
    weeks = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'learning_paths'


# ── F13: Peer Coding Rooms ────────────────────────────────────────────────────
class PeerRoom(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('closed', 'Closed')]

    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='peer_rooms_hosted')
    name = models.CharField(max_length=255)
    topic = models.CharField(max_length=255, blank=True, default='')
    language = models.CharField(max_length=50, default='JavaScript')
    difficulty = models.CharField(max_length=20, default='Medium')
    is_public = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    participants = models.JSONField(default=list)
    chat_log = models.JSONField(default=list)
    ratings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'peer_rooms'
        ordering = ['-created_at']


# ── F14: Reputation System ────────────────────────────────────────────────────
class ReputationScore(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reputation')
    total_score = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, default='Bronze')
    percentile = models.IntegerField(default=50)
    signals = models.JSONField(default=dict)
    history = models.JSONField(default=list)
    github_connected = models.BooleanField(default=False)
    github_username = models.CharField(max_length=100, blank=True, default='')
    leetcode_connected = models.BooleanField(default=False)
    leetcode_username = models.CharField(max_length=100, blank=True, default='')
    employer_endorsements = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reputation_scores'
