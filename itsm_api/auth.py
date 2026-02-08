"""
Authentication API - JWT authentication endpoints
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with user details"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['organization_id'] = user.organization_id
        token['is_superuser'] = user.is_superuser
        
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    """Token obtain view with custom serializer"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint - returns access and refresh tokens
    
    Request:
        {
            "username": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "user@example.com",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "organization_id": 1
            }
        }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=username)
    except User.DoesNotExist:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'User account is inactive'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims - convert UUID to string for JSON serialization
    refresh['user_id'] = str(user.id)
    refresh['organization_id'] = str(user.organization_id) if user.organization_id else None
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'organization_id': str(user.organization_id) if user.organization_id else None,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint - blacklists the refresh token
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'detail': 'Successfully logged out'
        }, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh access token using refresh token
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        
        return Response({
            'access': str(token.access_token),
            'refresh': str(token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password
    
    Request:
        {
            "old_password": "old_password123",
            "new_password": "new_password123",
            "confirm_password": "new_password123"
        }
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([old_password, new_password, confirm_password]):
        return Response({
            'error': 'All password fields are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != confirm_password:
        return Response({
            'error': 'New passwords do not match'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Old password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(new_password) < 8:
        return Response({
            'error': 'Password must be at least 8 characters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'detail': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify current access token
    
    Returns:
        {
            "valid": true,
            "user_id": 1,
            "username": "user@example.com",
            "organization_id": 1
        }
    """
    return Response({
        'valid': True,
        'user_id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'organization_id': request.user.organization_id
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_mfa(request):
    """
    Enable MFA for current user
    
    Request:
        {
            "mfa_method": "totp"
        }
    
    Response:
        {
            "secret": "JBSWY3DPEBLW64TMMQ======",
            "qr_code": "data:image/png;base64,..."
        }
    """
    user = request.user
    mfa_method = request.data.get('mfa_method', 'totp')
    
    if mfa_method == 'totp':
        import pyotp
        
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Store temporary secret for verification
        request.session['pending_mfa_secret'] = secret
        
        return Response({
            'secret': secret,
            'mfa_method': 'totp',
            'message': 'Scan QR code with authenticator app. Verify in next step.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Unsupported MFA method'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_mfa(request):
    """
    Verify and enable MFA with TOTP code
    
    Request:
        {
            "totp_code": "123456"
        }
    """
    user = request.user
    totp_code = request.data.get('totp_code')
    
    if not totp_code:
        return Response({
            'error': 'TOTP code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        pending_secret = request.session.get('pending_mfa_secret')
        if not pending_secret:
            return Response({
                'error': 'No pending MFA setup found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        import pyotp
        totp = pyotp.TOTP(pending_secret)
        
        if not totp.verify(totp_code):
            return Response({
                'error': 'Invalid TOTP code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save MFA settings
        user.mfa_enabled = True
        user.mfa_method = 'totp'
        user.mfa_secret = pending_secret
        user.save()
        
        # Clean up session
        del request.session['pending_mfa_secret']
        
        return Response({
            'detail': 'MFA enabled successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_mfa(request):
    """Disable MFA for current user"""
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response({
            'error': 'Password is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(password):
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user.mfa_enabled = False
    user.mfa_method = None
    user.mfa_secret = None
    user.save()
    
    return Response({
        'detail': 'MFA disabled successfully'
    }, status=status.HTTP_200_OK)
