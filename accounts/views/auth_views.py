from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from accounts.models import User, Employer
from accounts.serializers import RegisterSerializer, LoginSerializer, UserSerializer
from notifications.models import Notification


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'message': list(serializer.errors.values())[0][0]}, status=400)

    data = serializer.validated_data
    email = data['email'].lower()

    if User.objects.filter(email=email).exists():
        return Response({'message': 'Email already exists'}, status=400)

    is_employer = data['role'] == 'employer'
    user = User.objects.create_user(
        email=email,
        name=data['name'],
        password=data['password'],
        role=data['role'],
        is_approved=not is_employer,
        approval_status='pending' if is_employer else 'approved',
    )

    if is_employer and data.get('company_name'):
        Employer.objects.create(user=user, company_name=data['company_name'])
        # Notify all admins
        admins = User.objects.filter(role='admin')
        notifs = [
            Notification(
                recipient=admin,
                type='employer_pending',
                title='New Employer Registration',
                message=f"{user.name} ({data['company_name']}) has registered as an employer and is awaiting approval.",
                link='/admin/employers',
                related_user=user,
            )
            for admin in admins
        ]
        if notifs:
            Notification.objects.bulk_create(notifs)

    token = get_tokens_for_user(user)
    user_data = UserSerializer(user).data
    return Response({'token': token, 'user': user_data}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'message': 'Invalid data'}, status=400)

    data = serializer.validated_data
    user = User.objects.filter(email=data['email'].lower()).first()

    if not user or not user.check_password(data['password']):
        return Response({'message': 'Invalid credentials'}, status=400)

    if user.role == 'employer' and user.approval_status == 'rejected':
        return Response(
            {'message': 'Your employer account has been rejected. Please contact support.'},
            status=403
        )

    token = get_tokens_for_user(user)
    user_data = UserSerializer(user).data
    return Response({'token': token, 'user': user_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    return Response(UserSerializer(request.user).data)
