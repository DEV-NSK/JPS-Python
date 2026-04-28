from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from features.models import ReadinessScore
from features.views.copilot_views import compute_readiness_score


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_score(request):
    score, dims, badge = compute_readiness_score(request.user)
    all_latest = list(ReadinessScore.objects.values('user').distinct())
    lower = ReadinessScore.objects.filter(score__lt=score).values('user').distinct().count()
    percentile = round((lower / len(all_latest)) * 100) if all_latest else 50
    ReadinessScore.objects.create(user=request.user, score=score, dimensions=dims, badge=badge, percentile=percentile)
    return Response({'score': score, 'percentile': percentile, 'badge': badge, 'dimensions': dims})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    history = list(ReadinessScore.objects.filter(user=request.user).order_by('-created_at')[:30])
    history.reverse()
    return Response([{'day': i + 1, 'score': h.score, 'date': h.created_at} for i, h in enumerate(history)])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_improvements(request):
    _, dims, _ = compute_readiness_score(request.user)
    improvements = []
    action_map = {
        'Basic Info': 'Complete your bio, location, and phone number',
        'Skills Listed': 'Add more skills to your profile',
        'Assessments': 'Complete a skill assessment in your target domain',
        'Work Experience': 'Add your work experience with descriptions',
        'Projects': 'Add 2 more projects to your portfolio',
        'GitHub Activity': 'Connect your GitHub account',
        'LeetCode Stats': 'Solve 10 more LeetCode problems',
        'Peer Endorsements': 'Request endorsements from peers',
    }
    for dim in dims:
        if dim['score'] < 80:
            gap = 80 - dim['score']
            gain = max(1, round((gap / 100) * dim['weight']))
            improvements.append({
                'action': action_map.get(dim['name'], f"Improve your {dim['name']}"),
                'gain': gain,
                'effort': 'Medium' if gain > 5 else 'Low',
                'dimension': dim['name'],
            })
    improvements.sort(key=lambda x: -x['gain'])
    return Response(improvements[:4])
