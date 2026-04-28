from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q

from .models import Job, Bookmark
from .serializers import JobSerializer, JobCreateSerializer
from accounts.models import Employer
from accounts.permissions import IsEmployer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_jobs(request):
    search = request.query_params.get('search', '')
    location = request.query_params.get('location', '')
    job_type = request.query_params.get('type', '')
    category = request.query_params.get('category', '')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 10))

    qs = Job.objects.filter(is_active=True)
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(company_name__icontains=search) |
            Q(description__icontains=search)
        )
    if location:
        qs = qs.filter(location__icontains=location)
    if job_type:
        qs = qs.filter(type=job_type)
    if category:
        qs = qs.filter(category__icontains=category)

    total = qs.count()
    jobs = qs[(page - 1) * limit: page * limit]
    serializer = JobSerializer(jobs, many=True, context={'request': request})
    return Response({
        'jobs': serializer.data,
        'total': total,
        'pages': (total + limit - 1) // limit,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_job(request, job_id):
    try:
        job = Job.objects.select_related('employer').get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)
    return Response(JobSerializer(job, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_employer_jobs(request, employer_id):
    jobs = Job.objects.filter(employer_id=employer_id, is_active=True).order_by('-created_at')
    return Response(JobSerializer(jobs, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_job(request):
    employer = Employer.objects.filter(user=request.user).first()
    serializer = JobCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'message': str(serializer.errors)}, status=400)
    job = serializer.save(
        employer=request.user,
        company_name=employer.company_name if employer else request.user.name,
        company_logo=employer.company_logo if employer else '',
    )
    return Response(JobSerializer(job, context={'request': request}).data, status=201)


@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsEmployer])
def update_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id, employer=request.user)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)
    serializer = JobCreateSerializer(job, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response({'message': str(serializer.errors)}, status=400)
    job = serializer.save()
    return Response(JobSerializer(job, context={'request': request}).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job(request, job_id):
    if request.user.role == 'admin':
        Job.objects.filter(id=job_id).delete()
    else:
        Job.objects.filter(id=job_id, employer=request.user).delete()
    return Response({'message': 'Job deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bookmark_job(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)
    _, created = Bookmark.objects.get_or_create(user=request.user, job=job)
    if not created:
        return Response({'message': 'Job already bookmarked'}, status=400)
    return Response({'message': 'Job bookmarked successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unbookmark_job(request, job_id):
    Bookmark.objects.filter(user=request.user, job_id=job_id).delete()
    return Response({'message': 'Job unbookmarked successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookmarked_jobs(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('job').order_by('-created_at')
    jobs = []
    for b in bookmarks:
        data = JobSerializer(b.job, context={'request': request}).data
        data['is_bookmarked'] = True
        jobs.append(data)
    return Response({'jobs': jobs, 'total': len(jobs)})
