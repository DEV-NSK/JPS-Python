from datetime import date, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from features.models import LearningPath
from features.views.coding_views import record_activity

DEFAULT_WEEKS_FRONTEND = [
    {'week': 1, 'title': 'JavaScript Fundamentals', 'completed': False, 'current': True,
     'objectives': ['Closures & Scope', 'Promises & Async/Await', 'ES6+ Features'],
     'resources': [
         {'title': 'JavaScript: The Hard Parts', 'platform': 'Frontend Masters', 'time': '4h', 'type': 'video', 'url': 'https://frontendmasters.com', 'done': False},
         {'title': 'JS30 Challenge', 'platform': 'Wes Bos', 'time': '3h', 'type': 'practice', 'url': 'https://javascript30.com', 'done': False},
     ]},
    {'week': 2, 'title': 'React Advanced Patterns', 'completed': False, 'current': False,
     'objectives': ['Custom Hooks', 'Context & State Management', 'Performance Optimization'],
     'resources': [
         {'title': 'Advanced React Patterns', 'platform': 'Kent C. Dodds', 'time': '5h', 'type': 'course', 'url': 'https://epicreact.dev', 'done': False},
     ]},
    {'week': 3, 'title': 'TypeScript Mastery', 'completed': False, 'current': False,
     'objectives': ['Generics', 'Utility Types', 'Type Guards'],
     'resources': [
         {'title': 'TypeScript Handbook', 'platform': 'Official Docs', 'time': '3h', 'type': 'docs', 'url': 'https://typescriptlang.org', 'done': False},
     ]},
    {'week': 4, 'title': 'System Design Basics', 'completed': False, 'current': False,
     'objectives': ['Scalability Concepts', 'Database Design', 'API Design'],
     'resources': [
         {'title': 'System Design Primer', 'platform': 'GitHub', 'time': '6h', 'type': 'docs', 'url': 'https://github.com/donnemartin/system-design-primer', 'done': False},
     ]},
    {'week': 5, 'title': 'Testing & Quality', 'completed': False, 'current': False,
     'objectives': ['Unit Testing', 'Integration Testing', 'E2E Testing'],
     'resources': [
         {'title': 'Testing JavaScript', 'platform': 'Kent C. Dodds', 'time': '4h', 'type': 'course', 'url': 'https://testingjavascript.com', 'done': False},
     ]},
    {'week': 6, 'title': 'Performance & Optimization', 'completed': False, 'current': False,
     'objectives': ['Core Web Vitals', 'Bundle Optimization', 'Caching'],
     'resources': [
         {'title': 'Web Performance Fundamentals', 'platform': 'Frontend Masters', 'time': '3h', 'type': 'video', 'url': 'https://frontendmasters.com', 'done': False},
     ]},
    {'week': 7, 'title': 'Interview Preparation', 'completed': False, 'current': False,
     'objectives': ['LeetCode Practice', 'System Design Mock', 'Behavioural Questions'],
     'resources': [
         {'title': 'LeetCode Top 150', 'platform': 'LeetCode', 'time': '10h', 'type': 'practice', 'url': 'https://leetcode.com', 'done': False},
     ]},
    {'week': 8, 'title': 'Final Review & Applications', 'completed': False, 'current': False,
     'objectives': ['Portfolio Polish', 'Resume Update', 'Apply to Target Roles'],
     'resources': [
         {'title': 'Portfolio Review Checklist', 'platform': 'Platform', 'time': '2h', 'type': 'docs', 'url': '#', 'done': False},
     ]},
]

DEFAULT_WEEKS_BACKEND = [
    {'week': 1, 'title': 'Python/Django Deep Dive', 'completed': False, 'current': True,
     'objectives': ['ORM Mastery', 'REST APIs', 'Authentication'],
     'resources': [
         {'title': 'Django Documentation', 'platform': 'Official Docs', 'time': '4h', 'type': 'docs', 'url': 'https://docs.djangoproject.com', 'done': False},
     ]},
    {'week': 2, 'title': 'Database Design', 'completed': False, 'current': False,
     'objectives': ['SQL Optimization', 'Indexing', 'Transactions'],
     'resources': [
         {'title': 'PostgreSQL Tutorial', 'platform': 'Official Docs', 'time': '3h', 'type': 'docs', 'url': 'https://postgresql.org', 'done': False},
     ]},
    {'week': 3, 'title': 'API Design & Security', 'completed': False, 'current': False,
     'objectives': ['REST Best Practices', 'Authentication', 'Rate Limiting'],
     'resources': [
         {'title': 'OWASP Security Guide', 'platform': 'OWASP', 'time': '3h', 'type': 'docs', 'url': 'https://owasp.org', 'done': False},
     ]},
    {'week': 4, 'title': 'Microservices & Messaging', 'completed': False, 'current': False,
     'objectives': ['Service Design', 'Kafka Basics', 'Docker'],
     'resources': [
         {'title': 'Docker Getting Started', 'platform': 'Official Docs', 'time': '2h', 'type': 'docs', 'url': 'https://docker.com', 'done': False},
     ]},
    {'week': 5, 'title': 'System Design', 'completed': False, 'current': False,
     'objectives': ['Scalability', 'Caching', 'Load Balancing'],
     'resources': [
         {'title': 'System Design Interview', 'platform': 'Book', 'time': '8h', 'type': 'reading', 'url': '#', 'done': False},
     ]},
    {'week': 6, 'title': 'Cloud & DevOps', 'completed': False, 'current': False,
     'objectives': ['AWS Basics', 'CI/CD', 'Monitoring'],
     'resources': [
         {'title': 'AWS Free Tier', 'platform': 'AWS', 'time': '5h', 'type': 'practice', 'url': 'https://aws.amazon.com', 'done': False},
     ]},
    {'week': 7, 'title': 'Interview Preparation', 'completed': False, 'current': False,
     'objectives': ['System Design Practice', 'Coding Challenges', 'Behavioural'],
     'resources': [
         {'title': 'LeetCode Top 150', 'platform': 'LeetCode', 'time': '10h', 'type': 'practice', 'url': 'https://leetcode.com', 'done': False},
     ]},
    {'week': 8, 'title': 'Final Review', 'completed': False, 'current': False,
     'objectives': ['Portfolio', 'Resume', 'Applications'],
     'resources': [
         {'title': 'Resume Optimization', 'platform': 'Platform', 'time': '1h', 'type': 'practice', 'url': '#', 'done': False},
     ]},
]


def get_default_path(target_role):
    if 'frontend' in target_role.lower():
        return [dict(w) for w in DEFAULT_WEEKS_FRONTEND]
    return [dict(w) for w in DEFAULT_WEEKS_BACKEND]


def estimate_ready_date(total_days):
    d = date.today() + timedelta(days=total_days)
    return d.strftime('%B %d, %Y')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_path(request):
    path = LearningPath.objects.filter(user=request.user).first()
    if not path:
        return Response(None)
    return Response({
        'id': path.id, 'targetRole': path.target_role, 'totalDays': path.total_days,
        'currentDay': path.current_day, 'estimatedReadyDate': path.estimated_ready_date,
        'isFastTrack': path.is_fast_track, 'weeks': path.weeks,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_path(request):
    target_role = request.data.get('targetRole', '')
    is_fast_track = request.data.get('isFastTrack', False)
    if not target_role:
        return Response({'message': 'Target role required'}, status=400)

    total_days = 30 if is_fast_track else 60
    weeks = get_default_path(target_role)

    if settings.OPENAI_API_KEY:
        try:
            import json
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{
                    'role': 'system',
                    'content': f'Create a {total_days}-day learning path for {target_role}. Return JSON: {{weeks: [{{week, title, objectives: [], resources: [{{title, platform, time, type, url}}]}}]}}'
                }, {'role': 'user', 'content': f'Generate learning path for: {target_role}'}],
                max_tokens=1500,
            )
            parsed = json.loads(completion.choices[0].message.content)
            if parsed.get('weeks'):
                weeks = parsed['weeks']
                for i, w in enumerate(weeks):
                    w['completed'] = False
                    w['current'] = (i == 0)
                    for r in w.get('resources', []):
                        r['done'] = False
        except Exception:
            pass

    path, _ = LearningPath.objects.update_or_create(
        user=request.user,
        defaults={
            'target_role': target_role, 'total_days': total_days,
            'current_day': 1, 'is_fast_track': is_fast_track,
            'estimated_ready_date': estimate_ready_date(total_days),
            'weeks': weeks,
        }
    )
    return Response({
        'id': path.id, 'targetRole': path.target_role, 'totalDays': path.total_days,
        'estimatedReadyDate': path.estimated_ready_date, 'weeks': path.weeks,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_resource_complete(request, week_index, resource_index):
    path = LearningPath.objects.filter(user=request.user).first()
    if not path:
        return Response({'message': 'No learning path found'}, status=404)

    wi, ri = int(week_index), int(resource_index)
    weeks = path.weeks or []
    if wi < len(weeks) and ri < len(weeks[wi].get('resources', [])):
        weeks[wi]['resources'][ri]['done'] = not weeks[wi]['resources'][ri].get('done', False)
        if all(r.get('done') for r in weeks[wi]['resources']):
            weeks[wi]['completed'] = True
            if wi + 1 < len(weeks):
                weeks[wi]['current'] = False
                weeks[wi + 1]['current'] = True
        path.weeks = weeks
        path.save()
        record_activity(request.user, 'coursesProgressed')

    return Response({'id': path.id, 'weeks': path.weeks})
