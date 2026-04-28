from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from features.models import ResumeMatch

TECH_KEYWORDS = [
    'react', 'node.js', 'nodejs', 'javascript', 'typescript', 'python', 'java', 'c++', 'go',
    'aws', 'docker', 'kubernetes', 'mongodb', 'postgresql', 'redis', 'graphql', 'rest api',
    'git', 'agile', 'scrum', 'ci/cd', 'microservices', 'sql', 'nosql', 'html', 'css',
    'vue', 'angular', 'next.js', 'express', 'django', 'flask', 'spring', 'kafka',
    'terraform', 'jenkins', 'linux', 'bash', 'system design', 'machine learning',
    'data structures', 'algorithms', 'oop', 'testing', 'jest', 'cypress',
]


def extract_keywords(text):
    lower = text.lower()
    return [k for k in TECH_KEYWORDS if k in lower]


def compute_match_score(resume_kw, jd_kw):
    if not jd_kw:
        return 70
    matches = [k for k in resume_kw if k in jd_kw]
    return min(99, round(50 + (len(matches) / len(jd_kw)) * 50))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze(request):
    job_description = request.data.get('jobDescription', '')
    job_url = request.data.get('jobUrl', '')
    job_title = request.data.get('jobTitle', 'Job Position')

    if not job_description and not job_url:
        return Response({'message': 'Job description or URL required'}, status=400)

    user = request.user
    jd_text = job_description or ''
    resume_text = ' '.join(filter(None, [
        user.bio or '',
        ' '.join(user.skills or []),
        ' '.join(f"{e.get('title','')} {e.get('company','')} {e.get('description','')}"
                 for e in (user.experience or [])),
    ]))

    jd_kw = extract_keywords(jd_text)
    resume_kw = extract_keywords(resume_text)
    match_score = compute_match_score(resume_kw, jd_kw)
    keyword_matches = [k for k in resume_kw if k in jd_kw]
    keyword_missing = [k for k in jd_kw if k not in resume_kw]
    hard_skills_missing = [k.title() for k in keyword_missing[:5]]
    ats_probability = min(95, round(match_score * 0.9))
    domain_overlap = min(99, match_score + 5)

    suggestions = [
        {'original': 'Generic experience description',
         'improved': f"Highlight experience with {', '.join(keyword_missing[:3])} — these are explicitly required in the job description"},
        {'original': 'Worked on various projects',
         'improved': 'Led development of 3 production features serving 50k+ users, reducing load time by 40%'},
        {'original': 'Collaborated with team members',
         'improved': 'Partnered with cross-functional teams of 8+ engineers to deliver 4 major product milestones on schedule'},
    ] if keyword_missing else [
        {'original': 'Good match!', 'improved': 'Your profile already matches well. Focus on quantifying achievements.'}
    ]

    if settings.OPENAI_API_KEY and len(jd_text) > 100:
        try:
            import json
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'You are a resume expert. Return JSON: {"suggestions": [{"original": "...", "improved": "..."}]}'},
                    {'role': 'user', 'content': f'JD: {jd_text[:500]}\nSkills: {", ".join(user.skills or [])}\nMissing: {", ".join(keyword_missing)}'},
                ],
                max_tokens=400,
            )
            parsed = json.loads(completion.choices[0].message.content)
            if parsed.get('suggestions'):
                suggestions = parsed['suggestions']
        except Exception:
            pass

    saved = ResumeMatch.objects.create(
        user=user,
        job_title=job_title,
        job_description=jd_text[:2000],
        job_url=job_url or '',
        match_score=match_score,
        ats_probability=ats_probability,
        domain_overlap=domain_overlap,
        hard_skills_missing=hard_skills_missing,
        soft_skills_missing=['Cross-functional collaboration'],
        experience_delta='Verify experience requirements match your background',
        keyword_matches=[k.title() for k in keyword_matches],
        keyword_missing=[k.title() for k in keyword_missing],
        resume_suggestions=suggestions,
    )

    return Response({
        'id': saved.id, 'jobTitle': saved.job_title, 'matchScore': saved.match_score,
        'atsProbability': saved.ats_probability, 'domainOverlap': saved.domain_overlap,
        'hardSkillsMissing': saved.hard_skills_missing, 'softSkillsMissing': saved.soft_skills_missing,
        'keywordMatches': saved.keyword_matches, 'keywordMissing': saved.keyword_missing,
        'resumeSuggestions': saved.resume_suggestions, 'createdAt': saved.created_at,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved(request):
    analyses = ResumeMatch.objects.filter(user=request.user).values(
        'id', 'job_title', 'match_score', 'created_at', 'job_url'
    )[:20]
    return Response(list(analyses))


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_notes(request, match_id):
    ResumeMatch.objects.filter(id=match_id, user=request.user).update(notes=request.data.get('notes', ''))
    match = ResumeMatch.objects.get(id=match_id)
    return Response({'id': match.id, 'notes': match.notes})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_analysis(request, match_id):
    ResumeMatch.objects.filter(id=match_id, user=request.user).delete()
    return Response({'success': True})
