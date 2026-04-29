from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer
from accounts.models import User
from accounts.permissions import IsAdmin


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    if request.method == 'DELETE':
        Notification.objects.filter(recipient=request.user).delete()
        return Response({'success': True})
    notifs = Notification.objects.filter(recipient=request.user)[:50]
    return Response(NotificationSerializer(notifs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'count': count})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_read(request, notif_id):
    Notification.objects.filter(id=notif_id, recipient=request.user).update(is_read=True)
    return Response({'success': True})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notif_id):
    Notification.objects.filter(id=notif_id, recipient=request.user).delete()
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=True).delete()
    return Response({'success': True})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all(request):
    Notification.objects.filter(recipient=request.user).delete()
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def get_pending_employers(request):
    from accounts.serializers import UserSerializer
    pending = User.objects.filter(role='employer', approval_status='pending').order_by('-created_at')
    return Response(UserSerializer(pending, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def handle_employer_approval(request):
    user_id = request.data.get('userId') or request.data.get('user_id')
    action = request.data.get('action')  # 'approve' or 'reject'

    try:
        employer = User.objects.get(id=user_id, role='employer')
    except User.DoesNotExist:
        return Response({'message': 'Employer not found'}, status=404)

    employer.approval_status = 'approved' if action == 'approve' else 'rejected'
    employer.is_approved = action == 'approve'
    employer.save()

    Notification.objects.create(
        recipient=employer,
        type='employer_approved' if action == 'approve' else 'employer_rejected',
        title='Account Approved ✅' if action == 'approve' else 'Account Rejected ❌',
        message=(
            'Your employer account has been approved. You can now post jobs and hire candidates.'
            if action == 'approve'
            else 'Your employer account registration was not approved. Please contact support.'
        ),
        link='/employer/dashboard' if action == 'approve' else '/',
    )

    return Response({'success': True, 'approval_status': employer.approval_status})
