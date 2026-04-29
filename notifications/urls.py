from django.urls import path
from .views import (
    get_notifications, get_unread_count, mark_read, mark_all_read,
    delete_notification, delete_all_read, clear_all,
    get_pending_employers, handle_employer_approval,
)

urlpatterns = [
    path('', get_notifications),                              # GET /notifications  |  DELETE /notifications (clearAll)
    path('unread-count', get_unread_count),                   # GET /notifications/unread-count
    path('<int:notif_id>/read', mark_read),                   # PUT /notifications/:id/read
    path('mark-all-read', mark_all_read),                     # PUT /notifications/mark-all-read
    path('<int:notif_id>', delete_notification),              # DELETE /notifications/:id
    path('read', delete_all_read),                            # DELETE /notifications/read
    path('admin/pending-employers', get_pending_employers),
    path('admin/employer-approval', handle_employer_approval),
]
