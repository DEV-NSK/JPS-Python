from datetime import date, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from features.models import ActivityLog, UserStreak


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_heatmap(request):
    """Return last 365 days of activity as a heatmap."""
    end = date.today()
    start = end - timedelta(days=364)
    logs = ActivityLog.objects.filter(user=request.user, date__gte=start)
    counts = {}
    for log in logs:
        key = str(log.date)
        counts[key] = counts.get(key, 0) + 1

    heatmap = []
    current = start
    while current <= end:
        key = str(current)
        heatmap.append({'date': key, 'count': counts.get(key, 0)})
        current += timedelta(days=1)

    return Response({'heatmap': heatmap})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_streak(request):
    streak, _ = UserStreak.objects.get_or_create(user=request.user)
    today = date.today()
    # Check if streak is still active
    if streak.last_activity_date and streak.last_activity_date < today - timedelta(days=1):
        streak.current_streak = 0
        streak.save()
    return Response({
        'currentStreak': streak.current_streak,
        'longestStreak': streak.longest_streak,
        'lastActivityDate': str(streak.last_activity_date) if streak.last_activity_date else None,
        'dailyGoal': streak.daily_goal,
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_goal(request):
    goal = request.data.get('goal', 1)
    streak, _ = UserStreak.objects.get_or_create(user=request.user)
    streak.daily_goal = goal
    streak.save()
    return Response({'dailyGoal': streak.daily_goal})
