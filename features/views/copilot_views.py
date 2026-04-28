from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from features.models import CopilotGoal, ChatMessage, ReadinessScore
from accounts.models import User
from jobs.models import Job


def compute_readiness_score(user):
    dims = [
        {
            'name': 'Basic Info', 'weight': 10,
            'score': min(100, sum([
                20 if user.name else 0,
                20 if user.email else 0,
                20 if user.bio and len(user.bio) > 20 else 0,
                20 if user.location else 0,
                10 if user.phone else 0,
                10 if user.linkedin else 0,
            ]))
        },
        {'name': 'Skills Listed', 'weight': 15, 'score': min(100, len(user.skills or []) * 10)},
        {'name': 'Assessments', 'weight': 20, 'score': 40},
        {'name': 'Work Experience', 'weight': 20, 'score': min(100, len(user.experience or []) * 25)},
        {'name': 'Projects', 'weight': 15, 'score': 55},
        {'name': 'GitHub Activity', 'weight': 10, 'score': 70 if user.github else 0},
        {'name': 'LeetCode Stats', 'weight': 5, 'score': 45},
        {'name': 'Peer Endorsements', 'weight': 5, 'score': 30},
    ]
    score = round(sum((d['score'] / 100) * d['weight'] for d in dims))
    badge = 'Platinum' if score >= 86 else 'Gold' if score >= 71 else 'Silver' if score >= 41 else 'Bronze'
    return score, dims, badge


def generate_fallback_reply(message, user):
    msg = message.lower()
    if 'score' in msg or 'readiness' in msg:
        return 'Your readiness score reflects your profile completeness and activity. To improve it: add more skills, complete coding challenges daily, and fill in your work experience section.'
    if 'job' in msg or 'apply' in msg:
        return 'Focus on roles that match at least 70% of your skills. Tailor your resume for each application and highlight measurable achievements. Quality over quantity wins.'
    if 'skill' in msg or 'learn' in msg:
        return 'Based on current job market trends, System Design and TypeScript are high-demand skills worth investing in. Check your Learning Path for a structured roadmap.'
    if 'interview' in msg:
        return 'Practice daily with the Mock Interview Bot. Focus on the STAR method for behavioural questions and think out loud during technical problems.'
    return 'Great question! Focus on consistent daily practice — even 30 minutes a day compounds significantly over weeks. Check your Daily Coding section for today\'s recommended problems.'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_readiness(request):
    score, dims, badge = compute_readiness_score(request.user)
    scores = ReadinessScore.objects.filter(user=request.user).order_by('-created_at')
    delta = (scores[0].score - scores[1].score) if scores.count() >= 2 else 0
    ReadinessScore.objects.create(user=request.user, score=score, dimensions=dims, badge=badge)
    total = ReadinessScore.objects.values('user').distinct().count()
    lower = ReadinessScore.objects.filter(score__lt=score).values('user').distinct().count()
    percentile = round((lower / total) * 100) if total > 0 else 50
    return Response({'score': score, 'delta': delta, 'percentile': percentile, 'badge': badge, 'dimensions': dims, 'trend': 'up' if delta >= 0 else 'down'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_briefing(request):
    from django.conf import settings
    user = request.user
    goal = CopilotGoal.objects.filter(user=user).first()
    user_skills = user.skills or []

    top_jobs_qs = Job.objects.filter(is_active=True).order_by('-created_at')[:3]
    top_jobs = []
    for j in top_jobs_qs:
        job_skills = j.skills or []
        overlap = sum(1 for s in user_skills if any(s.lower() in js.lower() for js in job_skills))
        match = min(99, 60 + round((overlap / max(len(job_skills), 1)) * 40)) if user_skills else 75
        top_jobs.append({'title': j.title, 'company': j.company_name, 'match': match, 'location': j.location})

    scores = ReadinessScore.objects.filter(user=user).order_by('-created_at')[:2]
    delta = (scores[0].score - scores[1].score) if len(scores) >= 2 else 0

    return Response({
        'date': timezone.now().isoformat(),
        'delta': delta,
        'topJobs': top_jobs or [{'title': 'Software Engineer', 'company': 'Top Company', 'match': 80, 'location': 'Remote'}],
        'skillGaps': ['System Design', 'GraphQL'],
        'recommendedAction': 'Complete your profile to improve your readiness score',
        'insight': 'Remote engineering roles are up 18% this month — now is a great time to apply.',
        'targetRole': goal.target_role if goal else 'Software Engineer',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_goals(request):
    goal = CopilotGoal.objects.filter(user=request.user).first()
    if not goal:
        return Response({'targetRole': 'Software Engineer', 'timeline': '3 months', 'companyTier': 'Any'})
    return Response({'targetRole': goal.target_role, 'timeline': goal.timeline, 'companyTier': goal.company_tier, 'targetCompany': goal.target_company})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def set_goals(request):
    data = request.data
    goal, _ = CopilotGoal.objects.update_or_create(
        user=request.user,
        defaults={
            'target_role': data.get('targetRole', 'Software Engineer'),
            'timeline': data.get('timeline', '3 months'),
            'company_tier': data.get('companyTier', 'Any'),
            'target_company': data.get('targetCompany', ''),
        }
    )
    return Response({'targetRole': goal.target_role, 'timeline': goal.timeline, 'companyTier': goal.company_tier})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    messages = ChatMessage.objects.filter(user=request.user).order_by('created_at')[:50]
    return Response([{'id': m.id, 'role': m.role, 'text': m.text, 'rating': m.rating, 'createdAt': m.created_at} for m in messages])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    from django.conf import settings as django_settings
    message = request.data.get('message', '')
    if not message:
        return Response({'message': 'Message required'}, status=400)

    ChatMessage.objects.create(user=request.user, role='user', text=message)

    reply_text = generate_fallback_reply(message, request.user)

    if django_settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=django_settings.OPENAI_API_KEY)
            score, _, _ = compute_readiness_score(request.user)
            goal = CopilotGoal.objects.filter(user=request.user).first()
            history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:10]
            system_prompt = f"You are an AI Career Copilot. User: {request.user.name}, Skills: {', '.join(request.user.skills or [])}, Target Role: {goal.target_role if goal else 'Software Engineer'}, Readiness: {score}/100. Give concise career advice under 150 words."
            msgs = [{'role': 'system', 'content': system_prompt}]
            msgs += [{'role': m.role, 'content': m.text} for m in reversed(list(history))]
            msgs.append({'role': 'user', 'content': message})
            completion = client.chat.completions.create(model='gpt-3.5-turbo', messages=msgs, max_tokens=200)
            reply_text = completion.choices[0].message.content
        except Exception as e:
            pass

    reply = ChatMessage.objects.create(user=request.user, role='assistant', text=reply_text)
    return Response({'id': reply.id, 'role': 'assistant', 'text': reply_text})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_message(request, msg_id):
    ChatMessage.objects.filter(id=msg_id, user=request.user).update(rating=request.data.get('rating'))
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_score_history(request):
    history = list(ReadinessScore.objects.filter(user=request.user).order_by('-created_at')[:30])
    history.reverse()
    return Response([{'day': i + 1, 'score': h.score} for i, h in enumerate(history)])
