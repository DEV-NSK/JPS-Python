from django.urls import path
from .views import (
    get_jobs, get_job, get_employer_jobs, create_job,
    update_job, delete_job, bookmark_job, unbookmark_job, get_bookmarked_jobs
)

urlpatterns = [
    path('', get_jobs),
    path('bookmarked', get_bookmarked_jobs),
    path('employer/<int:employer_id>', get_employer_jobs),
    path('<int:job_id>', get_job),
    path('create', create_job),
    path('<int:job_id>/update', update_job),
    path('<int:job_id>/delete', delete_job),
    path('<int:job_id>/bookmark', bookmark_job),
    path('<int:job_id>/unbookmark', unbookmark_job),
]
