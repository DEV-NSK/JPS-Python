from django.urls import path
from .views import apply_job, get_user_applications, get_job_applications, update_status

urlpatterns = [
    path('apply', apply_job),
    path('user', get_user_applications),
    path('job/<int:job_id>', get_job_applications),
    path('status', update_status),
]
