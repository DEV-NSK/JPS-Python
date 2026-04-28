from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings

from .models import MicroInternship, MicroInternshipSubmission


@api_view(['GET'])
@permission_classes([AllowAny])
def get_marketplace(request):
    skills = request.query_params.get('skills', '')
    duration = request.query_params.get('duration', '')
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 12))

    qs = MicroInternship.objects.filter(status='active')
    if skills:
        skill_list = skills.split(',')
        from django.db.models import Q
        q = Q()
        for s in skill_list:
            q |= Q(skills__contains=[s.strip()])
        qs = qs.filter(q)
    if duration:
        qs = qs.filter(duration_days__lte=int(duration))

    total = qs.count()
    internships = qs[(page - 1) * limit: page * limit]

    return Response({
        'internships': [{
            'id': i.id, 'title': i.title, 'description': i.description,
            'skills': i.skills, 'durationDays': i.duration_days,
            'compensation': i.compensation, 'maxCandidates': i.max_candidates,
            'deliverable': i.deliverable, 'status': i.status,
            'applicantsCount': i.applicants.count(),
            'deadline': i.deadline, 'createdAt': i.created_at,
        } for i in internships],
        'total': total, 'page': page,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_internship(request):
    data = request.data
    duration_days = data.get('durationDays', 3)
    deadline = timezone.now() + timedelta(days=duration_days)
    internship = MicroInternship.objects.create(
        recruiter=request.user,
        title=data.get('title', ''),
        description=data.get('description', ''),
        skills=data.get('skills', []),
        duration_days=duration_days,
        compensation=data.get('compensation', ''),
        max_candidates=data.get('maxCandidates', 5),
        deliverable=data.get('deliverable', ''),
        rubric=data.get('rubric', ''),
        deadline=deadline,
    )
    return Response({'id': internship.id, 'title': internship.title}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_to_internship(request, internship_id):
    try:
        internship = MicroInternship.objects.get(id=internship_id)
    except MicroInternship.DoesNotExist:
        return Response({'message': 'Not found'}, status=404)
    if internship.applicants.filter(id=request.user.id).exists():
        return Response({'message': 'Already applied'}, status=400)
    internship.applicants.add(request.user)
    return Response({'message': 'Applied successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_candidate(request, internship_id, candidate_id):
    try:
        internship = MicroInternship.objects.get(id=internship_id)
    except MicroInternship.DoesNotExist:
        return Response({'message': 'Not found'}, status=404)
    if internship.accepted.count() >= internship.max_candidates:
        return Response({'message': 'Max candidates reached'}, status=400)
    internship.accepted.add(candidate_id)
    return Response({'message': 'Candidate accepted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_work(request, internship_id):
    try:
        internship = MicroInternship.objects.get(id=internship_id)
    except MicroInternship.DoesNotExist:
        return Response({'message': 'Not found'}, status=404)
    if internship.deadline and timezone.now() > internship.deadline:
        return Response({'message': 'Deadline passed'}, status=400)

    submission, _ = MicroInternshipSubmission.objects.get_or_create(
        internship=internship, candidate=request.user
    )
    submission.deliverable_text = request.data.get('deliverableText', '')
    submission.deliverable_url = request.data.get('deliverableUrl', '')
    submission.submitted_at = timezone.now()
    submission.save()

    # AI evaluation
    if settings.OPENAI_API_KEY and submission.deliverable_text and internship.rubric:
        try:
            import json
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': f'Evaluate submission against rubric.\nRubric: {internship.rubric}\nSubmission: {submission.deliverable_text[:500]}\nReturn JSON: {{"score": 0-100, "evaluation": "excellent|good|below_expectation", "feedback": "brief"}}'}],
                max_tokens=200,
            )
            result = json.loads(completion.choices[0].message.content)
            submission.score = result.get('score', 50)
            submission.evaluation = result.get('evaluation', 'good')
            submission.save()
        except Exception:
            pass

    return Response({
        'id': submission.id, 'score': submission.score,
        'evaluation': submission.evaluation, 'submittedAt': submission.submitted_at,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_submissions(request, internship_id):
    subs = MicroInternshipSubmission.objects.filter(internship_id=internship_id).select_related('candidate')
    return Response([{
        'id': s.id, 'score': s.score, 'evaluation': s.evaluation,
        'deliverableUrl': s.deliverable_url, 'submittedAt': s.submitted_at,
        'fastTracked': s.fast_tracked,
        'candidate': {'id': s.candidate.id, 'name': s.candidate.name,
                      'email': s.candidate.email, 'skills': s.candidate.skills},
    } for s in subs])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def evaluate_submission(request, internship_id, submission_id):
    MicroInternshipSubmission.objects.filter(id=submission_id).update(
        evaluation=request.data.get('evaluation', 'good'),
        recruiter_notes=request.data.get('recruiterNotes', ''),
    )
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fast_track(request, internship_id, candidate_id):
    MicroInternshipSubmission.objects.filter(
        internship_id=internship_id, candidate_id=candidate_id
    ).update(fast_tracked=True)
    return Response({'message': 'Fast-tracked to interview'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_internships(request):
    subs = MicroInternshipSubmission.objects.filter(candidate=request.user).select_related('internship')
    return Response([{
        'id': s.id, 'score': s.score, 'evaluation': s.evaluation,
        'submittedAt': s.submitted_at, 'fastTracked': s.fast_tracked,
        'internship': {'id': s.internship.id, 'title': s.internship.title,
                       'skills': s.internship.skills, 'status': s.internship.status},
    } for s in subs])
