from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone


@api_view(['GET'])
@permission_classes([AllowAny])
def root_view(request):
    return Response({
        'message': 'Job Portal API Running (Django)',
        'timestamp': timezone.now().isoformat(),
        'environment': 'development' if settings.DEBUG else 'production',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'OK', 'timestamp': timezone.now().isoformat()})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view),
    path('health', health_check),

    # Auth
    path('api/auth/', include('accounts.urls.auth_urls')),
    # Users
    path('api/users/', include('accounts.urls.user_urls')),
    # Jobs
    path('api/jobs/', include('jobs.urls')),
    # Applications
    path('api/applications/', include('applications.urls')),
    # Posts
    path('api/posts/', include('posts.urls')),
    # Employer
    path('api/employer/', include('accounts.urls.employer_urls')),
    # Admin
    path('api/admin/', include('accounts.urls.admin_urls')),
    # Notifications
    path('api/notifications/', include('notifications.urls')),
    # Features (14 features)
    path('api/', include('features.urls')),
    # Recruiter
    path('api/recruiter/', include('recruiter.urls')),
    # Marketplace
    path('api/marketplace/', include('marketplace.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    # Serve media files in production (when DEBUG=False)
    re_path(r'^uploads/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
