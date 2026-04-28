from django.urls import path
from accounts.views.employer_views import employer_jobs, employer_applications, employer_public_profile

urlpatterns = [
    path('jobs', employer_jobs),
    path('applications', employer_applications),
    path('profile/<int:employer_id>', employer_public_profile),
]
