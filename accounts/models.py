from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('approval_status', 'approved')
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('user', 'User'), ('employer', 'Employer'), ('admin', 'Admin')]
    APPROVAL_CHOICES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    avatar = models.CharField(max_length=500, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    skills = models.JSONField(default=list, blank=True)
    resume = models.CharField(max_length=500, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    linkedin = models.CharField(max_length=255, blank=True, default='')
    github = models.CharField(max_length=255, blank=True, default='')
    experience = models.JSONField(default=list, blank=True)   # [{title, company, duration, description}]
    education = models.JSONField(default=list, blank=True)    # [{degree, institution, year, description}]
    is_approved = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='approved')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.name} ({self.email})'


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255, blank=True, default='')
    company_logo = models.CharField(max_length=500, blank=True, default='')
    industry = models.CharField(max_length=255, blank=True, default='')
    company_size = models.CharField(max_length=100, blank=True, default='')
    website = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    culture = models.TextField(blank=True, default='')
    benefits = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    founded = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employers'

    def __str__(self):
        return self.company_name or self.user.name
