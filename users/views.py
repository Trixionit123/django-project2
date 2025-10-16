from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    if not username or not password:
        return Response({'detail': 'username and password required'}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({'detail': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})


@api_view(['GET', 'PUT'])
def profile(request):
    user = request.user
    if request.method == 'GET':
        return Response({'username': user.username, 'email': user.email, 'phone': getattr(user, 'phone', ''), 'address': getattr(user, 'address', '')})
    # PUT
    user.email = request.data.get('email', user.email)
    if hasattr(user, 'phone'):
        user.phone = request.data.get('phone', user.phone)
    if hasattr(user, 'address'):
        user.address = request.data.get('address', user.address)
    user.save()
    return Response({'detail': 'updated'})


