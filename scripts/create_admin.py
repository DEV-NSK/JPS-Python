"""
Create a superuser/admin account.
Run: python scripts/create_admin.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
django.setup()

from accounts.models import User

email = os.getenv('ADMIN_EMAIL', 'admin@jobportal.com')
password = os.getenv('ADMIN_PASSWORD', 'Admin@123456')
name = os.getenv('ADMIN_NAME', 'Admin')

if User.objects.filter(email=email).exists():
    print(f'Admin already exists: {email}')
else:
    User.objects.create_superuser(email=email, name=name, password=password)
    print(f'Admin created: {email} / {password}')
