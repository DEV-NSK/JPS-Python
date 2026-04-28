from django.urls import path
from .views import (
    get_marketplace, create_internship, apply_to_internship,
    accept_candidate, submit_work, get_submissions,
    evaluate_submission, fast_track, get_my_internships,
)

urlpatterns = [
    path('micro-internships', get_marketplace),
    path('micro-internships/create', create_internship),
    path('micro-internships/my', get_my_internships),
    path('micro-internships/<int:internship_id>/apply', apply_to_internship),
    path('micro-internships/<int:internship_id>/accept/<int:candidate_id>', accept_candidate),
    path('micro-internships/<int:internship_id>/submit', submit_work),
    path('micro-internships/<int:internship_id>/submissions', get_submissions),
    path('micro-internships/<int:internship_id>/evaluate/<int:submission_id>', evaluate_submission),
    path('micro-internships/<int:internship_id>/fast-track/<int:candidate_id>', fast_track),
]
