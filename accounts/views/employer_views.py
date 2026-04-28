from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from accounts.models import User, Employer
from accounts.permissions import IsEmployer
from accounts.serializers import EmployerSerializer, UserSerializer
from jobs.models import Job
from applications.models import Application
from applications.serializers import ApplicationSerializer
from jobs.serializers import JobSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_jobs(request):
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    return Response(JobSerializer(jobs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployer])
def employer_applications(request):
    job_ids = Job.objects.filter(employer=request.user).values_list('id', flat=True)
    apps = Application.objects.filter(job_id__in=job_ids).select_related(
        'job', 'applicant'
    ).order_by('-created_at')
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def employer_public_profile(request, employer_id):
    try:
        user = User.objects.get(id=employer_id, role='employer')
    except User.DoesNotExist:
        return Response({'message': 'Employer not found'}, status=404)

    employer = Employer.objects.filter(user=user).first()

    if not employer:
        job = Job.objects.filter(employer=user, is_active=True).first()
        basic = {
            'user_id': user.id,
            'company_name': job.company_name if job else user.name,
            'company_logo': job.company_logo if job else (user.avatar or ''),
            'location': job.location if job else '',
            'industry': job.category if job else '',
            'description': f"{job.company_name if job else user.name} is actively hiring.",
            'website': '', 'company_size': '', 'culture': '', 'benefits': '', 'founded': '',
        }
        return Response({'employer': basic})

    data = EmployerSerializer(employer).data
    if not data.get('company_logo') and user.avatar:
        data['company_logo'] = user.avatar
    return Response({'employer': data})
