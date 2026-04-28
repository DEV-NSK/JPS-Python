from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from jobs.models import Job


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_graph(request):
    user = request.user
    user_skills = user.skills or []

    # Build skill graph from job market data
    from django.db.models import Count
    job_skills_raw = Job.objects.filter(is_active=True).values_list('skills', flat=True)
    skill_counts = {}
    for skills_list in job_skills_raw:
        for s in (skills_list or []):
            skill_counts[s] = skill_counts.get(s, 0) + 1

    nodes = []
    for skill in user_skills:
        demand = skill_counts.get(skill, 0)
        nodes.append({
            'id': skill, 'label': skill, 'level': 'owned',
            'demand': demand, 'proficiency': 70,
        })

    # Add related skills not yet owned
    top_market = sorted(skill_counts.items(), key=lambda x: -x[1])[:10]
    for skill, demand in top_market:
        if skill not in user_skills:
            nodes.append({'id': skill, 'label': skill, 'level': 'missing', 'demand': demand, 'proficiency': 0})

    return Response({'nodes': nodes, 'edges': []})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_skill_detail(request, skill_id):
    from jobs.models import Job
    jobs_with_skill = Job.objects.filter(is_active=True, skills__contains=[skill_id]).count()
    return Response({
        'skill': skill_id,
        'jobsRequiring': jobs_with_skill,
        'averageSalary': 'Varies by role',
        'relatedSkills': [],
        'learningResources': [
            {'title': f'Learn {skill_id}', 'platform': 'Udemy', 'url': 'https://udemy.com'},
            {'title': f'{skill_id} Documentation', 'platform': 'Official Docs', 'url': '#'},
        ],
    })
