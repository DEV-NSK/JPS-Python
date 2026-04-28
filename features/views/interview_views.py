from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from features.models import InterviewRoom, MockInterviewSession
from features.views.coding_views import record_activity

HR_QUESTIONS = [
    'Tell me about yourself and your background.',
    'Why are you interested in this role?',
    'Describe a challenging project you worked on and how you overcame obstacles.',
    'How do you handle tight deadlines and competing priorities?',
    'Tell me about a time you disagreed with a team member. How did you resolve it?',
    'Where do you see yourself in 5 years?',
    'What is your greatest professional achievement?',
    'How do you stay updated with industry trends?',
    'Describe your ideal work environment.',
    'Why are you leaving your current role?',
]

TECHNICAL_QUESTIONS = {
    'Frontend': [
        'Explain the difference between var, let, and const in JavaScript.',
        'What is the virtual DOM and how does React use it?',
        'How would you optimize a slow React application?',
        'Explain CSS specificity and how it works.',
        'What are React hooks and why were they introduced?',
        'How does event delegation work in JavaScript?',
        'Explain the difference between synchronous and asynchronous JavaScript.',
        'What is CORS and how do you handle it?',
    ],
    'Backend': [
        'Explain RESTful API design principles.',
        'What is the difference between SQL and NoSQL databases?',
        'How does indexing work in databases?',
        'Explain the concept of middleware in Django.',
        'What is JWT and how does it work?',
        'How would you handle database transactions?',
        'Explain the difference between authentication and authorization.',
        'What is connection pooling and why is it important?',
    ],
    'DevOps': [
        'What is the difference between Docker and a virtual machine?',
        'Explain CI/CD pipeline design.',
        'What is Kubernetes and what problems does it solve?',
        'How would you monitor a production application?',
        'Explain blue-green deployment.',
        'What is infrastructure as code?',
        'How do you handle secrets management?',
        'Explain the 12-factor app methodology.',
    ],
}


def score_answer(question, answer, mode):
    from django.conf import settings
    if settings.OPENAI_API_KEY and answer and len(answer) > 20:
        try:
            from openai import OpenAI
            import json
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{
                    'role': 'system',
                    'content': f'Score this {"behavioural" if mode == "hr" else "technical"} answer 1-10 for clarity, depth, structure{"" if mode == "hr" else ", correctness"}. Return JSON: {{clarity, depth, structure{"" if mode == "hr" else ", correctness"}, overall, feedback}}'
                }, {'role': 'user', 'content': f'Q: {question}\nA: {answer}'}],
                max_tokens=200,
            )
            return json.loads(completion.choices[0].message.content)
        except Exception:
            pass
    words = len((answer or '').split())
    clarity = min(10, max(4, words // 15))
    depth = min(10, max(4, words // 20))
    structure = 8 if any(w in (answer or '').lower() for w in ['first', 'then', 'finally', 'because']) else 6
    overall = round((clarity + depth + structure) / 3, 1)
    return {'clarity': clarity, 'depth': depth, 'structure': structure, 'correctness': 7, 'overall': overall,
            'feedback': 'Good answer. Consider adding more specific examples and quantifiable results.'}


# ── Interview Rooms ───────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rooms(request):
    rooms = InterviewRoom.objects.filter(host=request.user).order_by('-created_at')[:20]
    return Response([{
        'id': r.id, 'title': r.title, 'status': r.status,
        'scheduledAt': r.scheduled_at, 'inviteeEmail': r.invitee_email,
        'createdAt': r.created_at,
    } for r in rooms])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    room = InterviewRoom.objects.create(
        host=request.user,
        title=request.data.get('title', 'Interview Room'),
        invitee_email=request.data.get('inviteeEmail', ''),
        recording_consent=request.data.get('recordingConsent', False),
    )
    return Response({'id': room.id, 'title': room.title, 'status': room.status}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_room(request, room_id):
    try:
        room = InterviewRoom.objects.get(id=room_id)
    except InterviewRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)
    return Response({'id': room.id, 'title': room.title, 'status': room.status, 'chatLog': room.chat_log, 'postSessionReport': room.post_session_report})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_room_status(request, room_id):
    InterviewRoom.objects.filter(id=room_id, host=request.user).update(status=request.data.get('status'))
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_report(request, room_id):
    InterviewRoom.objects.filter(id=room_id, host=request.user).update(
        post_session_report=request.data, status='completed'
    )
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_chat_message(request, room_id):
    try:
        room = InterviewRoom.objects.get(id=room_id)
    except InterviewRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)
    msg = {'sender': request.user.name, 'text': request.data.get('text', ''), 'time': timezone.now().isoformat()}
    room.chat_log = (room.chat_log or []) + [msg]
    room.save()
    return Response(msg)


# ── Mock Interview ────────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sessions(request):
    sessions = MockInterviewSession.objects.filter(user=request.user, status='completed').order_by('-created_at')[:10]
    return Response([{
        'id': s.id, 'mode': s.mode, 'role': s.role,
        'overallScore': s.overall_score, 'completedAt': s.completed_at, 'createdAt': s.created_at,
    } for s in sessions])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    mode = request.data.get('mode', 'hr')
    role = request.data.get('role', 'Frontend')
    questions = HR_QUESTIONS if mode == 'hr' else TECHNICAL_QUESTIONS.get(role, TECHNICAL_QUESTIONS['Frontend'])
    session = MockInterviewSession.objects.create(
        user=request.user, mode=mode, role=role,
        input_mode=request.data.get('inputMode', 'text'),
    )
    return Response({'sessionId': session.id, 'firstQuestion': questions[0], 'totalQuestions': len(questions)}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, session_id):
    try:
        session = MockInterviewSession.objects.get(id=session_id, user=request.user)
    except MockInterviewSession.DoesNotExist:
        return Response({'message': 'Session not found'}, status=404)

    questions = HR_QUESTIONS if session.mode == 'hr' else TECHNICAL_QUESTIONS.get(session.role, TECHNICAL_QUESTIONS['Frontend'])
    current_index = len(session.questions or [])
    current_question = questions[current_index] if current_index < len(questions) else questions[-1]
    answer = request.data.get('answer', '')
    scores = score_answer(current_question, answer, session.mode)

    session.questions = (session.questions or []) + [{
        'question': current_question, 'answer': answer,
        'scores': {'clarity': scores.get('clarity', 7), 'depth': scores.get('depth', 7),
                   'structure': scores.get('structure', 7), 'correctness': scores.get('correctness', 7)},
        'feedback': scores.get('feedback', ''), 'overall': scores.get('overall', 7),
    }]
    session.save()

    next_index = current_index + 1
    has_more = next_index < len(questions)
    return Response({
        'scores': scores,
        'nextQuestion': questions[next_index] if has_more else None,
        'questionNumber': next_index + 1,
        'totalQuestions': len(questions),
        'isComplete': not has_more,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request, session_id):
    try:
        session = MockInterviewSession.objects.get(id=session_id, user=request.user)
    except MockInterviewSession.DoesNotExist:
        return Response({'message': 'Session not found'}, status=404)

    qs = session.questions or []
    overall = round(sum(q.get('overall', 0) for q in qs) / len(qs), 1) if qs else 0
    session.status = 'completed'
    session.overall_score = overall
    session.completed_at = timezone.now()
    session.report = {
        'summary': f'You completed a {session.mode} interview for {session.role} with score {overall}/10.',
        'strengths': ['Clear communication', 'Relevant examples'],
        'improvements': ['Add more quantifiable results', 'Use STAR method'],
        'resources': [{'title': 'STAR Method Guide', 'type': 'Article', 'platform': 'Platform'}],
    }
    session.save()
    record_activity(request.user, 'mockInterviews')
    return Response({'success': True, 'overallScore': overall, 'sessionId': session.id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report(request, session_id):
    try:
        session = MockInterviewSession.objects.get(id=session_id, user=request.user)
    except MockInterviewSession.DoesNotExist:
        return Response({'message': 'Session not found'}, status=404)
    return Response({
        'id': session.id, 'mode': session.mode, 'role': session.role,
        'overallScore': session.overall_score, 'questions': session.questions,
        'report': session.report, 'completedAt': session.completed_at,
    })
