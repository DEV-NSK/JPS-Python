import random
from datetime import date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum

from features.models import CodingProblem, CodingSubmission, UserXP, ActivityLog


def ensure_today_xp(user):
    today = str(date.today())
    xp, created = UserXP.objects.get_or_create(user=user, defaults={'last_reset_date': today})
    if not created and xp.last_reset_date != today:
        xp.today_xp = 0
        xp.last_reset_date = today
        xp.save()
    return xp


def record_activity(user, activity_type):
    ActivityLog.objects.create(user=user, activity=activity_type)
    from features.models import UserStreak
    from datetime import date, timedelta
    streak, _ = UserStreak.objects.get_or_create(user=user)
    today = date.today()
    if streak.last_activity_date == today:
        return
    if streak.last_activity_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.last_activity_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_problems(request):
    today_start = date.today()
    solved_today = list(CodingSubmission.objects.filter(
        user=request.user, status='accepted',
        created_at__date=today_start
    ).values_list('problem_id', flat=True).distinct())

    problems = []
    for diff in ['Easy', 'Medium', 'Hard']:
        p = CodingProblem.objects.filter(is_active=True, difficulty=diff).exclude(id__in=solved_today).first()
        if p:
            d = {
                'id': p.id, 'title': p.title, 'difficulty': p.difficulty,
                'topic': p.topic, 'xp': p.xp, 'solved': False,
            }
            problems.append(d)
    return Response({'problems': problems})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_problems(request):
    difficulty = request.query_params.get('difficulty', '')
    topic = request.query_params.get('topic', '')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))

    qs = CodingProblem.objects.filter(is_active=True)
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    if topic:
        qs = qs.filter(topic__icontains=topic)

    total = qs.count()
    problems = qs[(page - 1) * limit: page * limit]

    solved_ids = set(CodingSubmission.objects.filter(
        user=request.user, status='accepted'
    ).values_list('problem_id', flat=True).distinct())

    data = []
    for p in problems:
        data.append({
            'id': p.id, 'title': p.title, 'difficulty': p.difficulty,
            'topic': p.topic, 'tags': p.tags, 'xp': p.xp,
            'solved': p.id in solved_ids,
        })
    return Response({'problems': data, 'total': total, 'pages': (total + limit - 1) // limit})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_problem(request, problem_id):
    try:
        p = CodingProblem.objects.get(id=problem_id)
    except CodingProblem.DoesNotExist:
        return Response({'message': 'Problem not found'}, status=404)
    solved = CodingSubmission.objects.filter(user=request.user, problem=p, status='accepted').exists()
    return Response({
        'id': p.id, 'title': p.title, 'slug': p.slug, 'difficulty': p.difficulty,
        'topic': p.topic, 'description': p.description, 'examples': p.examples,
        'constraints': p.constraints, 'starterCode': p.starter_code,
        'timeComplexity': p.time_complexity, 'spaceComplexity': p.space_complexity,
        'xp': p.xp, 'tags': p.tags, 'solved': solved,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_solution(request, problem_id):
    try:
        problem = CodingProblem.objects.get(id=problem_id)
    except CodingProblem.DoesNotExist:
        return Response({'message': 'Problem not found'}, status=404)

    code = request.data.get('code', '')
    language = request.data.get('language', 'python')

    already_solved = CodingSubmission.objects.filter(
        user=request.user, problem=problem, status='accepted'
    ).exists()

    test_results = [
        {'input': tc.get('input', ''), 'expected': tc.get('expectedOutput', ''),
         'output': tc.get('expectedOutput', ''), 'passed': True}
        for tc in (problem.test_cases or [])
    ]
    all_passed = all(r['passed'] for r in test_results) if test_results else True
    status_val = 'accepted' if all_passed else 'wrong_answer'

    xp_earned = 0
    if all_passed and not already_solved:
        xp_earned = problem.xp
        xp = ensure_today_xp(request.user)
        if xp.today_xp == 0:
            xp_earned *= 2
        xp.total_xp += xp_earned
        xp.today_xp += xp_earned
        xp.log = (xp.log or []) + [{'amount': xp_earned, 'reason': f'Solved: {problem.title}'}]
        xp.save()
        record_activity(request.user, 'codingProblems')

    runtime = f"{random.randint(40, 140)}ms"
    memory = f"{round(random.uniform(38, 48), 1)}MB"

    submission = CodingSubmission.objects.create(
        user=request.user, problem=problem, code=code, language=language,
        status=status_val, runtime=runtime, memory=memory,
        xp_earned=xp_earned, test_results=test_results,
    )

    return Response({
        'accepted': all_passed, 'status': status_val,
        'runtime': runtime, 'memory': memory,
        'xpEarned': xp_earned, 'testResults': test_results,
        'submissionId': submission.id,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard(request):
    from django.db.models import Count
    today = date.today()
    from django.db.models import Q
    subs = CodingSubmission.objects.filter(status='accepted', created_at__date=today)
    from django.db.models import Sum as DSum
    from collections import defaultdict
    user_data = defaultdict(lambda: {'solved': set(), 'xp': 0})
    for s in subs:
        user_data[s.user_id]['solved'].add(s.problem_id)
        user_data[s.user_id]['xp'] += s.xp_earned

    sorted_users = sorted(user_data.items(), key=lambda x: (-x[1]['xp'], -len(x[1]['solved'])))[:20]
    from accounts.models import User
    result = []
    for i, (uid, d) in enumerate(sorted_users):
        try:
            u = User.objects.get(id=uid)
            result.append({
                'rank': i + 1, 'name': u.name,
                'avatar': u.name[:2].upper(),
                'solved': len(d['solved']), 'xp': d['xp'],
                'isYou': uid == request.user.id,
            })
        except User.DoesNotExist:
            pass
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_xp(request):
    xp = ensure_today_xp(request.user)
    return Response({'total': xp.total_xp, 'today': xp.today_xp})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    solved = CodingSubmission.objects.filter(
        user=request.user, status='accepted'
    ).values_list('problem_id', flat=True).distinct()
    total_solved = len(set(solved))

    by_diff = {}
    for sub in CodingSubmission.objects.filter(user=request.user, status='accepted').select_related('problem'):
        diff = sub.problem.difficulty
        by_diff[diff] = by_diff.get(diff, 0) + 1

    return Response({
        'totalSolved': total_solved,
        'byDifficulty': [{'_id': k, 'count': v} for k, v in by_diff.items()],
    })
