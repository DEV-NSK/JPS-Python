from django.urls import path
from .views import (
    get_notifications, get_unread_count, mark_read, mark_all_read,
    delete_notification, delete_all_read, clear_all,
    get_pending_employers, handle_employer_approval,
)

urlpatterns = [
    path('', get_notifications),
    path('unread-count', get_unread_count),
    path('<int:notif_id>/read', mark_read),
    path('mark-all-read', mark_all_read),
    path('<int:notif_id>/delete', delete_notification),
    path('read/delete', delete_all_read),
    path('clear', clear_all),
    path('admin/pending-employers', get_pending_employers),
    path('admin/employer-approval', handle_employer_approval),
]
