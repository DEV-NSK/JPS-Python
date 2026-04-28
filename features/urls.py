from django.urls import path
from features.views.copilot_views import (
    get_readiness, get_briefing, get_goals, set_goals,
    get_chat_history, chat, rate_message, get_score_history,
)
from features.views.profile_score_views import get_score, get_history as ps_history, get_improvements
from features.views.skill_graph_views import get_graph, get_skill_detail
from features.views.resume_match_views import analyze as rm_analyze, get_saved, update_notes, delete_analysis
from features.views.consistency_views import get_heatmap, get_streak, set_goal
from features.views.coding_views import (
    get_daily_problems, get_problems, get_problem,
    submit_solution, get_leaderboard, get_xp, get_stats as coding_stats,
)
from features.views.interview_views import (
    get_rooms, create_room, get_room, update_room_status, save_report, add_chat_message,
    get_sessions, start_session, submit_answer, end_session, get_report,
)
from features.views.code_quality_views import analyze as cq_analyze, get_history as cq_history
from features.views.project_views import (
    get_projects, create_project, get_project, accept_project, submit_project, get_my_submissions,
)
from features.views.learning_views import get_path, generate_path, mark_resource_complete
from features.views.opportunity_views import get_opportunity_jobs, get_job_score
from features.views.peer_views import (
    get_lobby, create_room as create_peer_room, join_room, leave_room,
    send_chat, rate_session, switch_role,
)
from features.views.reputation_views import (
    get_reputation, get_public_profile, connect_github, connect_leetcode, request_endorsement,
)

urlpatterns = [
    # F1: AI Career Copilot
    path('copilot/readiness', get_readiness),
    path('copilot/briefing', get_briefing),
    path('copilot/goals', get_goals),
    path('copilot/goals/set', set_goals),
    path('copilot/chat/history', get_chat_history),
    path('copilot/chat', chat),
    path('copilot/chat/<int:msg_id>/rate', rate_message),
    path('copilot/score-history', get_score_history),

    # F2: Profile Strength Score
    path('profile-score', get_score),
    path('profile-score/history', ps_history),
    path('profile-score/improvements', get_improvements),

    # F3: Skill Graph
    path('skill-graph', get_graph),
    path('skill-graph/<str:skill_id>', get_skill_detail),

    # F4: Resume Match
    path('resume-match/analyze', rm_analyze),
    path('resume-match/saved', get_saved),
    path('resume-match/<int:match_id>/notes', update_notes),
    path('resume-match/<int:match_id>/delete', delete_analysis),

    # F5: Consistency Tracker
    path('consistency/heatmap', get_heatmap),
    path('consistency/streak', get_streak),
    path('consistency/goal', set_goal),

    # F6: Daily Coding Practice
    path('coding/daily', get_daily_problems),
    path('coding/problems', get_problems),
    path('coding/problems/<int:problem_id>', get_problem),
    path('coding/problems/<int:problem_id>/submit', submit_solution),
    path('coding/leaderboard', get_leaderboard),
    path('coding/xp', get_xp),
    path('coding/stats', coding_stats),

    # F7: Interview Rooms
    path('interview-rooms', get_rooms),
    path('interview-rooms/create', create_room),
    path('interview-rooms/<int:room_id>', get_room),
    path('interview-rooms/<int:room_id>/status', update_room_status),
    path('interview-rooms/<int:room_id>/report', save_report),
    path('interview-rooms/<int:room_id>/chat', add_chat_message),

    # F8: Code Quality Analyzer
    path('code-quality/analyze', cq_analyze),
    path('code-quality/history', cq_history),

    # F9: Project-Based Hiring
    path('projects', get_projects),
    path('projects/create', create_project),
    path('projects/my-submissions', get_my_submissions),
    path('projects/<int:project_id>', get_project),
    path('projects/<int:project_id>/accept', accept_project),
    path('projects/<int:project_id>/submit', submit_project),

    # F10: Mock Interview Bot
    path('mock-interview/sessions', get_sessions),
    path('mock-interview/start', start_session),
    path('mock-interview/<int:session_id>/answer', submit_answer),
    path('mock-interview/<int:session_id>/end', end_session),
    path('mock-interview/<int:session_id>/report', get_report),

    # F11: Learning Path
    path('learning-path', get_path),
    path('learning-path/generate', generate_path),
    path('learning-path/resources/<int:week_index>/<int:resource_index>/complete', mark_resource_complete),

    # F12: Opportunity Score
    path('opportunity/jobs', get_opportunity_jobs),
    path('opportunity/jobs/<int:job_id>/score', get_job_score),

    # F13: Peer Coding Rooms
    path('peer-rooms', get_lobby),
    path('peer-rooms/create', create_peer_room),
    path('peer-rooms/<int:room_id>/join', join_room),
    path('peer-rooms/<int:room_id>/leave', leave_room),
    path('peer-rooms/<int:room_id>/chat', send_chat),
    path('peer-rooms/<int:room_id>/rate', rate_session),
    path('peer-rooms/<int:room_id>/role', switch_role),

    # F14: Reputation System
    path('reputation', get_reputation),
    path('reputation/profile/<str:username>', get_public_profile),
    path('reputation/connect/github', connect_github),
    path('reputation/connect/leetcode', connect_leetcode),
    path('reputation/endorse', request_endorsement),
]
