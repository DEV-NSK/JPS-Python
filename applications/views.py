from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Application
from .serializers import ApplicationSerializer
from jobs.models import Job
from notifications.models import Notification


STATUS_LABELS = {
    'pending': 'Under Review',
    'reviewed': 'Reviewed',
    'accepted': 'Accepted 🎉',
    'rejected': 'Not Selected',
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_job(request):
    job_id = request.data.get('jobId') or request.data.get('job_id')
    cover_letter = request.data.get('coverLetter') or request.data.get('cover_letter', '')

    if Application.objects.filter(job_id=job_id, applicant=request.user).exists():
        return Response({'message': 'Already applied'}, status=400)

    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    application = Application.objects.create(
        job=job,
        applicant=request.user,
        cover_letter=cover_letter,
        resume=request.user.resume,
    )
    Job.objects.filter(id=job_id).update(applicants_count=job.applicants_count + 1)

    Notification.objects.create(
        recipient=job.employer,
        type='application_received',
        title='New Application Received',
        message=f'{request.user.name} applied for "{job.title}"',
        link=f'/employer/applicants/{job_id}',
        related_user=request.user,
    )

    return Response(ApplicationSerializer(application).data, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_applications(request):
    apps = Application.objects.filter(applicant=request.user).select_related(
        'job'
    ).order_by('-created_at')
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_applications(request, job_id):
    try:
        job = Job.objects.get(id=job_id, employer=request.user)
    except Job.DoesNotExist:
        return Response({'message': 'Not authorized'}, status=403)
    apps = Application.objects.filter(job=job).select_related('applicant').order_by('-created_at')
    return Response(ApplicationSerializer(apps, many=True).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_status(request):
    app_id = request.data.get('applicationId') or request.data.get('application_id')
    new_status = request.data.get('status')

    try:
        app = Application.objects.select_related('job', 'applicant').get(id=app_id)
    except Application.DoesNotExist:
        return Response({'message': 'Application not found'}, status=404)

    if str(app.job.employer_id) != str(request.user.id):
        return Response({'message': 'Not authorized'}, status=403)

    old_status = app.status
    app.status = new_status
    app.save()

    if old_status != new_status:
        label = STATUS_LABELS.get(new_status, new_status)
        messages = {
            'accepted': f'Congratulations! Your application for "{app.job.title}" at {app.job.company_name} has been accepted.',
            'rejected': f'Your application for "{app.job.title}" at {app.job.company_name} was not selected this time.',
            'reviewed': f'Your application for "{app.job.title}" at {app.job.company_name} is being reviewed.',
            'pending': f'Your application for "{app.job.title}" is back to pending review.',
        }
        Notification.objects.create(
            recipient=app.applicant,
            type='application_status',
            title=f'Application {label}',
            message=messages.get(new_status, f'Your application status changed to {label}.'),
            link='/applied',
        )

    return Response(ApplicationSerializer(app).data)
