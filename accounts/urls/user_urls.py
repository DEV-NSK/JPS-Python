from django.urls import path
from accounts.views.user_views import get_profile, update_profile, profile_view

urlpatterns = [
    path('profile', profile_view),              # GET + PUT on same URL
    path('profile/<int:user_id>', get_profile), # GET by ID
    path('profile/update', update_profile),     # PUT (legacy, keep for compat)
    path('resume', update_profile),
]
