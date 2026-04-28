from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from jobs.models import Job


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_opportunity_jobs(request):
    user = request.user
    user_skills = user.skills or []
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:20]
    result = []
    for j in jobs:
        job_skills = j.skills or []
        overlap = sum(1 for s in user_skills if any(s.lower() in js.lower() for js in job_skills))
        match = min(99, 60 + round((overlap / max(len(job_skills), 1)) * 40)) if user_skills else 70
        result.append({
            'id': j.id, 'title': j.title, 'companyName': j.company_name,
            'location': j.location, 'type': j.type, 'salary': j.salary,
            'matchScore': match, 'skills': job_skills,
        })
    result.sort(key=lambda x: -x['matchScore'])
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_score(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    user = request.user
    user_skills = user.skills or []
    job_skills = job.skills or []
    overlap = sum(1 for s in user_skills if any(s.lower() in js.lower() for js in job_skills))
    match = min(99, 60 + round((overlap / max(len(job_skills), 1)) * 40)) if user_skills else 70
    missing = [s for s in job_skills if not any(s.lower() in us.lower() for us in user_skills)]

    return Response({
        'jobId': job.id, 'matchScore': match,
        'matchedSkills': [s for s in user_skills if any(s.lower() in js.lower() for js in job_skills)],
        'missingSkills': missing[:5],
        'recommendation': 'Strong match! Apply now.' if match >= 80 else 'Good match. Consider upskilling in missing areas.',
    })
