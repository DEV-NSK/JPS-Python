import csv
import io
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse

from applications.models import Application
from jobs.models import Job
from recruiter.models import RecruiterPin, ShortlistAudit, CandidateTimeline, BlindHiringReveal, TalentPool
from accounts.models import User
from accounts.serializers import UserSerializer


# ── F11: Hiring Funnel ────────────────────────────────────────────────────────
FUNNEL_STAGES = ['applied', 'screened', 'shortlisted', 'interview_scheduled',
                 'interview_done', 'offer_extended', 'selected', 'rejected']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_funnel(request, job_id):
    from_date = request.query_params.get('from')
    to_date = request.query_params.get('to')

    qs = Application.objects.filter(job_id=job_id)
    if from_date:
        qs = qs.filter(created_at__gte=from_date)
    if to_date:
        qs = qs.filter(created_at__lte=to_date)

    apps = list(qs)
    stage_counts = {s: 0 for s in FUNNEL_STAGES}
    for a in apps:
        if a.funnel_stage in stage_counts:
            stage_counts[a.funnel_stage] += 1

    result = []
    for i, stage in enumerate(FUNNEL_STAGES):
        count = stage_counts[stage]
        prev = stage_counts[FUNNEL_STAGES[i - 1]] if i > 0 else count
        conversion = round((count / prev) * 100) if prev > 0 else 0
        result.append({'name': stage, 'count': count, 'conversionRate': conversion, 'avgDaysInStage': 2})

    return Response({'stages': result, 'total': len(apps)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stage_candidates(request, job_id, stage):
    apps = Application.objects.filter(job_id=job_id, funnel_stage=stage).select_related('applicant').order_by('-created_at')
    return Response([{
        'id': a.id, 'funnelStage': a.funnel_stage, 'status': a.status,
        'createdAt': a.created_at, 'isShortlisted': a.is_shortlisted,
        'applicant': {'id': a.applicant.id, 'name': a.applicant.name,
                      'email': a.applicant.email, 'skills': a.applicant.skills},
    } for a in apps])


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_stage(request, app_id):
    stage = request.data.get('stage')
    try:
        app = Application.objects.get(id=app_id)
    except Application.DoesNotExist:
        return Response({'message': 'Application not found'}, status=404)

    old_stage = app.funnel_stage
    history = app.stage_history or []
    history.append({'stage': old_stage, 'enteredAt': str(app.funnel_stage_entered_at), 'exitedAt': str(timezone.now())})
    app.stage_history = history
    app.funnel_stage = stage
    app.funnel_stage_entered_at = timezone.now()
    app.save()

    CandidateTimeline.objects.create(
        application=app, event_type='stage_changed',
        actor=request.user, actor_role='recruiter',
        details={'from': old_stage, 'to': stage}, is_recruiter_only=True,
    )
    return Response({'id': app.id, 'funnelStage': app.funnel_stage})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_funnel(request, job_id):
    apps = Application.objects.filter(job_id=job_id).select_related('applicant')
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Stage', 'Applied At'])
    for a in apps:
        writer.writerow([a.applicant.name, a.applicant.email, a.funnel_stage, a.created_at])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=funnel-{job_id}.csv'
    return response


# ── F12: Candidate Ranking ────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ranked_applicants(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    apps = Application.objects.filter(job=job).select_related('applicant').order_by('-ranking_score', '-created_at')
    required_skills = [s.get('skillName', '').lower() for s in (job.required_skills or [])]

    result = []
    for a in apps:
        user_skills = [s.lower() for s in (a.applicant.skills or [])]
        match = sum(1 for s in required_skills if s in user_skills)
        score = round((match / max(len(required_skills), 1)) * 100) if required_skills else 70
        if a.ranking_score == 0:
            a.ranking_score = score
            a.save(update_fields=['ranking_score'])
        pinned = RecruiterPin.objects.filter(recruiter=request.user, job=job, candidate=a.applicant).exists()
        result.append({
            'applicationId': a.id, 'rankingScore': score, 'isPinned': pinned,
            'funnelStage': a.funnel_stage, 'isShortlisted': a.is_shortlisted,
            'applicant': {'id': a.applicant.id, 'name': a.applicant.name,
                          'email': a.applicant.email, 'skills': a.applicant.skills,
                          'avatar': a.applicant.avatar},
        })
    result.sort(key=lambda x: (-x['isPinned'], -x['rankingScore']))
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pin_candidate(request):
    job_id = request.data.get('jobId')
    candidate_id = request.data.get('candidateId')
    RecruiterPin.objects.get_or_create(recruiter=request.user, job_id=job_id, candidate_id=candidate_id)
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unpin_candidate(request, job_id, candidate_id):
    RecruiterPin.objects.filter(recruiter=request.user, job_id=job_id, candidate_id=candidate_id).delete()
    return Response({'success': True})


# ── F14: Auto Shortlisting ────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_shortlist(request):
    job_id = request.data.get('jobId')
    threshold = request.data.get('threshold', 70)
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    required_skills = [s.get('skillName', '').lower() for s in (job.required_skills or [])]
    apps = Application.objects.filter(job=job, funnel_stage='applied').select_related('applicant')

    shortlisted = []
    for a in apps:
        user_skills = [s.lower() for s in (a.applicant.skills or [])]
        match = round((sum(1 for s in required_skills if s in user_skills) / max(len(required_skills), 1)) * 100) if required_skills else 70
        if match >= threshold:
            shortlisted.append({'applicationId': a.id, 'candidateName': a.applicant.name, 'matchScore': match})

    audit = ShortlistAudit.objects.create(job=job, candidates=shortlisted)
    return Response({'shortlisted': shortlisted, 'auditId': audit.id, 'total': len(shortlisted)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_shortlist(request):
    audit_id = request.data.get('auditId')
    try:
        audit = ShortlistAudit.objects.get(id=audit_id)
    except ShortlistAudit.DoesNotExist:
        return Response({'message': 'Audit not found'}, status=404)

    app_ids = [c['applicationId'] for c in (audit.candidates or [])]
    Application.objects.filter(id__in=app_ids).update(is_shortlisted=True, funnel_stage='shortlisted')
    audit.approved_by = request.user
    audit.approved_at = timezone.now()
    audit.save()
    return Response({'success': True, 'approvedCount': len(app_ids)})


# ── F15: Candidate Timeline ───────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_timeline(request, app_id):
    events = CandidateTimeline.objects.filter(application_id=app_id).order_by('created_at')
    return Response([{
        'id': e.id, 'eventType': e.event_type, 'details': e.details,
        'note': e.note, 'isRecruiterOnly': e.is_recruiter_only, 'createdAt': e.created_at,
    } for e in events])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_note(request, app_id):
    event = CandidateTimeline.objects.create(
        application_id=app_id, event_type='note',
        actor=request.user, actor_role='recruiter',
        note=request.data.get('note', ''), is_recruiter_only=True,
    )
    return Response({'id': event.id, 'note': event.note, 'createdAt': event.created_at})


# ── F16: Blind Hiring ─────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_blind_mode(request, job_id):
    try:
        job = Job.objects.get(id=job_id, employer=request.user)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)
    job.blind_mode = not job.blind_mode
    job.save()
    return Response({'blindMode': job.blind_mode})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reveal_identity(request):
    job_id = request.data.get('jobId')
    candidate_id = request.data.get('candidateId')
    reveal, created = BlindHiringReveal.objects.get_or_create(job_id=job_id, candidate_id=candidate_id)
    candidate = User.objects.filter(id=candidate_id).first()
    return Response({'revealed': True, 'candidate': UserSerializer(candidate).data if candidate else None})


# ── F17: Skill-Based Job Posting ──────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_skill_matches(request):
    job_id = request.data.get('jobId')
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    required = [s.get('skillName', '').lower() for s in (job.required_skills or [])]
    threshold = job.min_match_threshold or 70
    users = User.objects.filter(role='user')
    matches = []
    for u in users:
        user_skills = [s.lower() for s in (u.skills or [])]
        match = round((sum(1 for s in required if s in user_skills) / max(len(required), 1)) * 100) if required else 70
        if match >= threshold:
            matches.append({'userId': u.id, 'name': u.name, 'matchScore': match, 'skills': u.skills})
    matches.sort(key=lambda x: -x['matchScore'])
    return Response({'matches': matches[:20], 'total': len(matches)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_apply(request):
    job_id = request.data.get('jobId')
    from applications.models import Application
    from jobs.models import Job as JobModel
    try:
        job = JobModel.objects.get(id=job_id)
    except JobModel.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)
    if Application.objects.filter(job=job, applicant=request.user).exists():
        return Response({'message': 'Already applied'}, status=400)
    app = Application.objects.create(job=job, applicant=request.user, resume=request.user.resume)
    JobModel.objects.filter(id=job_id).update(applicants_count=job.applicants_count + 1)
    return Response({'id': app.id, 'message': 'Quick applied successfully'}, status=201)


# ── F18: Job Health ───────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_health(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

    apps = Application.objects.filter(job=job).count()
    health_score = min(100, 50 + apps * 5)
    tier = 'promoted' if health_score >= 80 else 'high' if health_score >= 60 else 'standard'
    return Response({
        'jobId': job.id, 'healthScore': health_score, 'tier': tier,
        'applicantsCount': apps, 'isUrgent': job.is_urgent, 'isHot': job.is_hot,
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def override_tier(request, job_id):
    tier = request.data.get('tier', 'standard')
    Job.objects.filter(id=job_id, employer=request.user).update(tier=tier)
    return Response({'success': True, 'tier': tier})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_health_overview(request):
    jobs = Job.objects.filter(employer=request.user)
    result = []
    for j in jobs:
        apps = Application.objects.filter(job=j).count()
        health = min(100, 50 + apps * 5)
        result.append({'jobId': j.id, 'title': j.title, 'healthScore': health, 'applicantsCount': apps})
    return Response(result)


# ── F20: Talent Pools ─────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pools(request):
    pools = TalentPool.objects.filter(recruiter=request.user).order_by('-created_at')
    return Response([{
        'id': p.id, 'name': p.name, 'description': p.description,
        'memberCount': len(p.members or []), 'isTeamVisible': p.is_team_visible,
        'createdAt': p.created_at,
    } for p in pools])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pool(request):
    pool = TalentPool.objects.create(
        recruiter=request.user,
        name=request.data.get('name', 'New Pool'),
        description=request.data.get('description', ''),
        is_team_visible=request.data.get('isTeamVisible', False),
    )
    return Response({'id': pool.id, 'name': pool.name}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pool_members(request, pool_id):
    try:
        pool = TalentPool.objects.get(id=pool_id, recruiter=request.user)
    except TalentPool.DoesNotExist:
        return Response({'message': 'Pool not found'}, status=404)
    members = pool.members or []
    result = []
    for m in members:
        user = User.objects.filter(id=m.get('candidateId')).first()
        if user:
            result.append({
                'candidateId': user.id, 'name': user.name, 'email': user.email,
                'skills': user.skills, 'notes': m.get('notes', ''),
                'rating': m.get('rating', 0), 'tags': m.get('tags', []),
            })
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, pool_id):
    try:
        pool = TalentPool.objects.get(id=pool_id, recruiter=request.user)
    except TalentPool.DoesNotExist:
        return Response({'message': 'Pool not found'}, status=404)
    candidate_id = request.data.get('candidateId')
    members = pool.members or []
    if not any(m.get('candidateId') == candidate_id for m in members):
        members.append({'candidateId': candidate_id, 'notes': '', 'rating': 0, 'tags': []})
        pool.members = members
        pool.save()
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, pool_id, candidate_id):
    try:
        pool = TalentPool.objects.get(id=pool_id, recruiter=request.user)
    except TalentPool.DoesNotExist:
        return Response({'message': 'Pool not found'}, status=404)
    pool.members = [m for m in (pool.members or []) if m.get('candidateId') != int(candidate_id)]
    pool.save()
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_pool(request, pool_id):
    TalentPool.objects.filter(id=pool_id, recruiter=request.user).delete()
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pool(request, pool_id):
    try:
        pool = TalentPool.objects.get(id=pool_id, recruiter=request.user)
    except TalentPool.DoesNotExist:
        return Response({'message': 'Pool not found'}, status=404)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Skills', 'Rating', 'Notes'])
    for m in (pool.members or []):
        user = User.objects.filter(id=m.get('candidateId')).first()
        if user:
            writer.writerow([user.name, user.email, ', '.join(user.skills or []), m.get('rating', 0), m.get('notes', '')])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=pool-{pool_id}.csv'
    return response
