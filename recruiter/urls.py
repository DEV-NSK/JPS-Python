from django.urls import path
from .views import (
    get_funnel, get_stage_candidates, update_stage, export_funnel,
    get_ranked_applicants, pin_candidate, unpin_candidate,
    auto_shortlist, approve_shortlist,
    get_timeline, add_note,
    toggle_blind_mode, reveal_identity,
    find_skill_matches, quick_apply,
    get_job_health, override_tier, get_health_overview,
    get_pools, create_pool, get_pool_members, add_member, remove_member, delete_pool, export_pool,
)

urlpatterns = [
    # Hiring Funnel
    path('jobs/<int:job_id>/funnel', get_funnel),
    path('jobs/<int:job_id>/funnel/<str:stage>/candidates', get_stage_candidates),
    path('applications/<int:app_id>/stage', update_stage),
    path('jobs/<int:job_id>/funnel/export', export_funnel),

    # Candidate Ranking
    path('jobs/<int:job_id>/applicants/ranked', get_ranked_applicants),
    path('pins', pin_candidate),
    path('pins/<int:job_id>/<int:candidate_id>', unpin_candidate),

    # Auto Shortlisting
    path('shortlist', auto_shortlist),
    path('shortlist/approve', approve_shortlist),

    # Candidate Timeline
    path('applications/<int:app_id>/timeline', get_timeline),
    path('applications/<int:app_id>/timeline/note', add_note),

    # Blind Hiring
    path('jobs/<int:job_id>/blind-mode', toggle_blind_mode),
    path('blind/reveal', reveal_identity),

    # Skill-Based Job Posting
    path('jobs/skill-match', find_skill_matches),
    path('quick-apply', quick_apply),

    # Job Health
    path('jobs/<int:job_id>/health', get_job_health),
    path('jobs/<int:job_id>/tier', override_tier),
    path('jobs/health-overview', get_health_overview),

    # Talent Pools
    path('talent-pools', get_pools),
    path('talent-pools/create', create_pool),
    path('talent-pools/<int:pool_id>/members', get_pool_members),
    path('talent-pools/<int:pool_id>/members/add', add_member),
    path('talent-pools/<int:pool_id>/members/<int:candidate_id>', remove_member),
    path('talent-pools/<int:pool_id>', delete_pool),
    path('talent-pools/<int:pool_id>/export', export_pool),
]
