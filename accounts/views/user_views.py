import os
import json
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.conf import settings

from accounts.models import User, Employer
from accounts.serializers import UserSerializer, EmployerSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request, user_id=None):
    try:
        target_id = user_id or request.user.id
        user = User.objects.get(id=target_id)
        employer = None
        if user.role == 'employer':
            employer = Employer.objects.filter(user=user).first()
        return Response({
            'user': UserSerializer(user).data,
            'employer': EmployerSerializer(employer).data if employer else None,
        })
    except User.DoesNotExist:
        return Response({'message': 'User not found'}, status=404)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def profile_view(request):
    """Handles GET and PUT on /api/users/profile"""
    if request.method == 'GET':
        user = request.user
        employer = None
        if user.role == 'employer':
            employer = Employer.objects.filter(user=user).first()
        return Response({
            'user': UserSerializer(user).data,
            'employer': EmployerSerializer(employer).data if employer else None,
        })
    return update_profile(request)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_profile(request):
    user = request.user
    data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)

    # Handle file upload
    if request.FILES.get('avatar'):
        file = request.FILES['avatar']
        data['avatar'] = _save_file(file, 'avatars')
    if request.FILES.get('resume'):
        file = request.FILES['resume']
        data['resume'] = _save_file(file, 'resumes')

    # Parse JSON fields
    for field in ('experience', 'education'):
        if field in data and isinstance(data[field], str):
            try:
                data[field] = json.loads(data[field])
            except (json.JSONDecodeError, TypeError):
                data[field] = []

    # Parse skills
    if 'skills' in data and isinstance(data['skills'], str):
        data['skills'] = [s.strip() for s in data['skills'].split(',') if s.strip()]

    # Employer-specific fields
    employer_fields = [
        'company_name', 'company_logo', 'industry', 'company_size',
        'website', 'description', 'culture', 'benefits', 'founded'
    ]
    employer_data = {k: data.pop(k) for k in employer_fields if k in data}

    # Remove immutable fields
    for f in ('password', 'role', 'id', 'created_at', 'updated_at',
              'createdAt', 'updatedAt', 'isSuperuser', 'is_superuser',
              'isStaff', 'is_staff', 'isActive', 'isApproved', 'approvalStatus'):
        data.pop(f, None)

    # Update user
    for attr, value in data.items():
        if hasattr(user, attr):
            setattr(user, attr, value)
    user.save()

    # Update employer profile
    if user.role == 'employer' and employer_data:
        if data.get('location'):
            employer_data['location'] = data['location']
        if data.get('avatar'):
            employer_data['company_logo'] = data['avatar']
        Employer.objects.update_or_create(user=user, defaults=employer_data)
    elif user.role == 'employer' and data.get('avatar'):
        Employer.objects.update_or_create(user=user, defaults={'company_logo': data['avatar']})

    return Response(UserSerializer(user).data)


def _save_file(file, subfolder):
    """Save uploaded file locally and return URL path."""
    if settings.USE_CLOUDINARY:
        import cloudinary.uploader
        resource_type = 'raw' if file.name.lower().endswith(('.pdf', '.doc', '.docx')) else 'image'
        result = cloudinary.uploader.upload(file, folder='job-portal', resource_type=resource_type)
        return result.get('secure_url', '')
    else:
        upload_dir = settings.MEDIA_ROOT / subfolder
        upload_dir.mkdir(parents=True, exist_ok=True)
        import time
        filename = f"{int(time.time() * 1000)}-{file.name.replace(' ', '_')}"
        filepath = upload_dir / filename
        with open(filepath, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        return f"/uploads/{subfolder}/{filename}"
