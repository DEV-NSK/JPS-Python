from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from features.models import PeerRoom
from features.views.coding_views import record_activity


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lobby(request):
    rooms = PeerRoom.objects.filter(status='active', is_public=True).order_by('-created_at')[:20]
    result = []
    for r in rooms:
        participants = r.participants or []
        result.append({
            'id': r.id, 'name': r.name, 'topic': r.topic, 'language': r.language,
            'difficulty': r.difficulty, 'hostId': r.host_id,
            'participantCount': len(participants), 'maxParticipants': r.max_participants,
            'isFull': len(participants) >= r.max_participants,
            'createdAt': r.created_at,
        })
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    data = request.data
    room = PeerRoom.objects.create(
        host=request.user,
        name=data.get('name', 'Peer Room'),
        topic=data.get('topic', ''),
        language=data.get('language', 'JavaScript'),
        difficulty=data.get('difficulty', 'Medium'),
        is_public=data.get('isPublic', True),
        max_participants=data.get('maxParticipants', 4),
        participants=[{'userId': request.user.id, 'name': request.user.name, 'role': 'Driver'}],
    )
    return Response({'id': room.id, 'name': room.name, 'status': room.status}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_room(request, room_id):
    try:
        room = PeerRoom.objects.get(id=room_id)
    except PeerRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)

    if room.status != 'active':
        return Response({'message': 'Room is closed'}, status=400)

    participants = room.participants or []
    if len(participants) >= room.max_participants:
        return Response({'message': 'Room is full'}, status=400)

    already_in = any(p.get('userId') == request.user.id for p in participants)
    if not already_in:
        roles = ['Driver', 'Navigator', 'Observer']
        taken = [p.get('role') for p in participants]
        role = next((r for r in roles if r not in taken), 'Observer')
        participants.append({'userId': request.user.id, 'name': request.user.name, 'role': role})
        room.participants = participants
        room.save()

    return Response({'id': room.id, 'participants': room.participants})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_room(request, room_id):
    try:
        room = PeerRoom.objects.get(id=room_id)
    except PeerRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)

    participants = [p for p in (room.participants or []) if p.get('userId') != request.user.id]
    room.participants = participants
    if room.host_id == request.user.id or not participants:
        room.status = 'closed'
    room.save()
    record_activity(request.user, 'peerReviews')
    return Response({'success': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat(request, room_id):
    try:
        room = PeerRoom.objects.get(id=room_id)
    except PeerRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)

    msg = {
        'senderId': request.user.id,
        'senderName': request.user.name,
        'text': request.data.get('text', ''),
        'time': timezone.now().isoformat(),
    }
    room.chat_log = (room.chat_log or []) + [msg]
    room.save()
    return Response(msg)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_session(request, room_id):
    try:
        room = PeerRoom.objects.get(id=room_id)
    except PeerRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)

    rating = {
        'raterId': request.user.id,
        'ratedUserId': request.data.get('ratedUserId'),
        'score': request.data.get('score', 5),
    }
    room.ratings = (room.ratings or []) + [rating]
    room.save()
    return Response({'success': True})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def switch_role(request, room_id):
    try:
        room = PeerRoom.objects.get(id=room_id)
    except PeerRoom.DoesNotExist:
        return Response({'message': 'Room not found'}, status=404)

    new_role = request.data.get('role', 'Observer')
    participants = room.participants or []
    for p in participants:
        if p.get('userId') == request.user.id:
            p['role'] = new_role
    room.participants = participants
    room.save()
    return Response({'success': True})
