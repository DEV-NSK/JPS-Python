import re
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from features.models import CodeQualityResult


def analyze_code_locally(code, language):
    """Basic static analysis without external tools."""
    issues = []
    suggestions = []
    lines = code.split('\n')
    line_count = len(lines)

    # Check for long lines
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            issues.append({'line': i, 'type': 'style', 'message': f'Line {i} exceeds 100 characters'})

    # Check for TODO/FIXME
    for i, line in enumerate(lines, 1):
        if 'TODO' in line or 'FIXME' in line:
            issues.append({'line': i, 'type': 'warning', 'message': f'Unresolved TODO/FIXME on line {i}'})

    # Check for console.log / print statements
    debug_pattern = r'console\.log|print\(' if language in ('javascript', 'python') else r'System\.out\.print'
    for i, line in enumerate(lines, 1):
        if re.search(debug_pattern, line):
            issues.append({'line': i, 'type': 'warning', 'message': f'Debug statement found on line {i}'})

    # Scores
    readability = max(40, min(100, 100 - len(issues) * 5))
    maintainability = max(40, min(100, 90 - (line_count // 50) * 5))
    performance = 75
    security = 80
    overall = round((readability + maintainability + performance + security) / 4)

    if line_count > 100:
        suggestions.append('Consider breaking this into smaller functions for better maintainability')
    if not any('def ' in l or 'function ' in l or 'const ' in l for l in lines[:5]):
        suggestions.append('Add a module-level docstring or comment explaining the purpose')
    suggestions.append('Consider adding unit tests for critical logic paths')

    return overall, readability, maintainability, performance, security, issues, suggestions


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze(request):
    code = request.data.get('code', '')
    language = request.data.get('language', 'python').lower()

    if not code:
        return Response({'message': 'Code is required'}, status=400)

    overall, readability, maintainability, performance, security, issues, suggestions = \
        analyze_code_locally(code, language)

    if settings.OPENAI_API_KEY:
        try:
            import json
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{
                    'role': 'system',
                    'content': 'Analyze this code and return JSON: {"overall": 0-100, "readability": 0-100, "maintainability": 0-100, "performance": 0-100, "security": 0-100, "issues": [{"line": n, "type": "error|warning|style", "message": "..."}], "suggestions": ["..."]}'
                }, {'role': 'user', 'content': f'Language: {language}\n\n{code[:1500]}'}],
                max_tokens=500,
            )
            parsed = json.loads(completion.choices[0].message.content)
            overall = parsed.get('overall', overall)
            readability = parsed.get('readability', readability)
            maintainability = parsed.get('maintainability', maintainability)
            performance = parsed.get('performance', performance)
            security = parsed.get('security', security)
            issues = parsed.get('issues', issues)
            suggestions = parsed.get('suggestions', suggestions)
        except Exception:
            pass

    result = CodeQualityResult.objects.create(
        user=request.user, code=code, language=language,
        overall_score=overall, readability=readability,
        maintainability=maintainability, performance=performance,
        security=security, issues=issues, suggestions=suggestions,
    )

    return Response({
        'id': result.id, 'overallScore': result.overall_score,
        'readability': result.readability, 'maintainability': result.maintainability,
        'performance': result.performance, 'security': result.security,
        'issues': result.issues, 'suggestions': result.suggestions,
        'createdAt': result.created_at,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    results = CodeQualityResult.objects.filter(user=request.user).values(
        'id', 'language', 'overall_score', 'created_at'
    )[:20]
    return Response(list(results))
