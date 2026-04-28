from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from features.models import Project, ProjectSubmission
from accounts.permissions import IsEmployer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_projects(request):
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    return Response([{
        'id': p.id, 'title': p.title, 'company': p.company, 'companyLogo': p.company_logo,
        'domain': p.domain, 'difficulty': p.difficulty, 'durationHours': p.duration_hours,
        'reward': p.reward, 'techStack': p.tech_stack, 'description': p.description,
        'submissionsCount': p.submissions_count, 'createdAt': p.created_at,
    } for p in projects])


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEmployer])
def create_project(request):
    data = request.data
    project = Project.objects.create(
        employer=request.user,
        title=data.get('title', ''),
        company=data.get('company', ''),
        domain=data.get('domain', ''),
        difficulty=data.get('difficulty', 'Medium'),
        duration_hours=data.get('durationHours', 4),
        reward=data.get('reward', ''),
        tech_stack=data.get('techStack', []),
        description=data.get('description', ''),
        requirements=data.get('requirements', []),
        starter_code_url=data.get('starterCodeUrl', ''),
    )
    return Response({'id': project.id, 'title': project.title}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, project_id):
    try:
        p = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'message': 'Project not found'}, status=404)
    return Response({
        'id': p.id, 'title': p.title, 'company': p.company, 'description': p.description,
        'requirements': p.requirements, 'techStack': p.tech_stack, 'difficulty': p.difficulty,
        'durationHours': p.duration_hours, 'reward': p.reward, 'starterCodeUrl': p.starter_code_url,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_project(request, project_id):
    # Mark user as accepted (just acknowledge)
    return Response({'message': 'Project accepted. Start working on it!'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'message': 'Project not found'}, status=404)

    submission, created = ProjectSubmission.objects.update_or_create(
        project=project, candidate=request.user,
        defaults={
            'code': request.data.get('code', ''),
            'repo_url': request.data.get('repoUrl', ''),
        }
    )
    if created:
        Project.objects.filter(id=project_id).update(submissions_count=project.submissions_count + 1)
    return Response({'id': submission.id, 'message': 'Submission received'}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_submissions(request):
    subs = ProjectSubmission.objects.filter(candidate=request.user).select_related('project')
    return Response([{
        'id': s.id, 'projectTitle': s.project.title, 'score': s.score,
        'feedback': s.feedback, 'submittedAt': s.submitted_at,
    } for s in subs])
