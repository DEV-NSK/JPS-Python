import requests as http_requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings

from features.models import ReputationScore, UserXP, PeerRoom
from accounts.models import User


def get_tier(score):
    if score >= 751:
        return 'Platinum'
    if score >= 501:
        return 'Gold'
    if score >= 251:
        return 'Silver'
    return 'Bronze'


def compute_reputation(user):
    rep, _ = ReputationScore.objects.get_or_create(user=user, defaults={'signals': {
        'githubActivity': {'score': 0, 'max': 200, 'trend': 0},
        'leetcodeRank': {'score': 0, 'max': 200, 'trend': 0},
        'platformXP': {'score': 0, 'max': 200, 'trend': 0},
        'peerRatings': {'score': 0, 'max': 200, 'trend': 0},
        'employerEndorsements': {'score': 0, 'max': 200, 'trend': 0},
    }})

    signals = rep.signals or {}

    # Platform XP
    xp_obj = UserXP.objects.filter(user=user).first()
    platform_xp_score = min(200, round((xp_obj.total_xp if xp_obj else 0) / 10))

    # Peer ratings
    peer_score = signals.get('peerRatings', {}).get('score', 0)
    all_ratings = []
    for room in PeerRoom.objects.all():
        for r in (room.ratings or []):
            if r.get('ratedUserId') == user.id:
                all_ratings.append(r.get('score', 5))
    if all_ratings:
        avg = sum(all_ratings) / len(all_ratings)
        peer_score = min(200, round(avg * 20 * min(1, len(all_ratings) / 5)))

    github_score = signals.get('githubActivity', {}).get('score', 0)
    leetcode_score = signals.get('leetcodeRank', {}).get('score', 0)
    endorsement_score = min(200, len([e for e in (rep.employer_endorsements or []) if e.get('verified')]) * 40)

    total = platform_xp_score + github_score + leetcode_score + peer_score + endorsement_score
    tier = get_tier(total)

    all_reps = list(ReputationScore.objects.values_list('total_score', flat=True))
    lower = sum(1 for s in all_reps if s < total)
    percentile = round((lower / len(all_reps)) * 100) if all_reps else 50

    from django.utils import timezone
    this_month = timezone.now().strftime('%b')
    history = rep.history or []
    if not history or history[-1].get('month') != this_month:
        history.append({'month': this_month, 'score': total})
        if len(history) > 12:
            history = history[-12:]

    rep.total_score = total
    rep.tier = tier
    rep.percentile = percentile
    rep.signals = {
        'githubActivity': {'score': github_score, 'max': 200, 'trend': 0},
        'leetcodeRank': {'score': leetcode_score, 'max': 200, 'trend': 0},
        'platformXP': {'score': platform_xp_score, 'max': 200, 'trend': 0},
        'peerRatings': {'score': peer_score, 'max': 200, 'trend': 0},
        'employerEndorsements': {'score': endorsement_score, 'max': 200, 'trend': 0},
    }
    rep.history = history
    rep.save()
    return rep


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reputation(request):
    rep = compute_reputation(request.user)
    signals = rep.signals or {}
    return Response({
        'score': rep.total_score, 'tier': rep.tier, 'percentile': rep.percentile,
        'signals': [
            {'name': 'GitHub Activity', 'score': signals.get('githubActivity', {}).get('score', 0), 'max': 200, 'trend': 0, 'icon': 'github'},
            {'name': 'LeetCode Rank', 'score': signals.get('leetcodeRank', {}).get('score', 0), 'max': 200, 'trend': 0, 'icon': 'code'},
            {'name': 'Platform XP', 'score': signals.get('platformXP', {}).get('score', 0), 'max': 200, 'trend': 0, 'icon': 'xp'},
            {'name': 'Peer Ratings', 'score': signals.get('peerRatings', {}).get('score', 0), 'max': 200, 'trend': 0, 'icon': 'star'},
            {'name': 'Employer Endorsements', 'score': signals.get('employerEndorsements', {}).get('score', 0), 'max': 200, 'trend': 0, 'icon': 'award'},
        ],
        'history': rep.history,
        'githubConnected': rep.github_connected,
        'leetcodeConnected': rep.leetcode_connected,
        'githubUsername': rep.github_username,
        'leetcodeUsername': rep.leetcode_username,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_profile(request, username):
    user = User.objects.filter(name__icontains=username).first()
    if not user:
        return Response({'message': 'User not found'}, status=404)
    rep = ReputationScore.objects.filter(user=user).first()
    if not rep:
        return Response({'message': 'Reputation not found'}, status=404)
    return Response({
        'user': {'name': user.name, 'avatar': user.avatar},
        'score': rep.total_score, 'tier': rep.tier,
        'percentile': rep.percentile, 'history': rep.history,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_github(request):
    username = request.data.get('username', '')
    if not username:
        return Response({'message': 'GitHub username required'}, status=400)

    github_score = 50
    commits, stars = 0, 0
    try:
        headers = {'User-Agent': 'JobPortal-Django'}
        if settings.GITHUB_TOKEN:
            headers['Authorization'] = f'token {settings.GITHUB_TOKEN}'
        resp = http_requests.get(f'https://api.github.com/users/{username}', headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            github_score = min(200, data.get('public_repos', 0) * 3 + data.get('followers', 0) * 2)
            stars = data.get('public_repos', 0) * 2
    except Exception:
        pass

    rep, _ = ReputationScore.objects.get_or_create(user=request.user)
    signals = rep.signals or {}
    signals['githubActivity'] = {'score': github_score, 'max': 200, 'trend': 0}
    rep.signals = signals
    rep.github_connected = True
    rep.github_username = username
    rep.save()
    compute_reputation(request.user)
    return Response({'success': True, 'githubScore': github_score, 'username': username, 'stars': stars})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def connect_leetcode(request):
    username = request.data.get('username', '')
    if not username:
        return Response({'message': 'LeetCode username required'}, status=400)

    leetcode_score = 50
    solved, rating = 0, 0
    try:
        resp = http_requests.post(
            'https://leetcode.com/graphql',
            json={'query': 'query($u:String!){matchedUser(username:$u){submitStats{acSubmissionNum{difficulty count}}profile{ranking}}}', 'variables': {'u': username}},
            headers={'Content-Type': 'application/json', 'Referer': 'https://leetcode.com'},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json().get('data', {}).get('matchedUser', {})
            if data:
                stats = data.get('submitStats', {}).get('acSubmissionNum', [])
                solved = sum(s.get('count', 0) for s in stats)
                rating = data.get('profile', {}).get('ranking', 0)
                leetcode_score = min(200, round(solved * 0.5 + (max(0, 200 - rating / 1000) if rating else 0)))
    except Exception:
        pass

    rep, _ = ReputationScore.objects.get_or_create(user=request.user)
    signals = rep.signals or {}
    signals['leetcodeRank'] = {'score': leetcode_score, 'max': 200, 'trend': 0}
    rep.signals = signals
    rep.leetcode_connected = True
    rep.leetcode_username = username
    rep.save()
    compute_reputation(request.user)
    return Response({'success': True, 'leetcodeScore': leetcode_score, 'username': username, 'solved': solved})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_endorsement(request):
    target_user_id = request.data.get('targetUserId')
    message = request.data.get('message', '')
    try:
        rep, _ = ReputationScore.objects.get_or_create(user_id=target_user_id)
        endorsements = rep.employer_endorsements or []
        endorsements.append({
            'employerId': request.user.id,
            'companyName': request.user.name,
            'message': message,
            'verified': False,
        })
        rep.employer_endorsements = endorsements
        rep.save()
    except Exception:
        pass
    return Response({'success': True, 'message': 'Endorsement request sent.'})
