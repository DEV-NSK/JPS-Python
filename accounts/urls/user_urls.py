from django.urls import path
from accounts.views.user_views import get_profile, update_profile

urlpatterns = [
    path('profile', get_profile),
    path('profile/<int:user_id>', get_profile),
    path('profile/update', update_profile),
    path('resume', update_profile),
]
