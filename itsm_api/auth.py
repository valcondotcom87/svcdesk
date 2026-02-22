"""
Authentication API - JWT authentication endpoints
"""
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.db.models import Q

from apps.users.models import User
from apps.audit.models import AuditLog
from apps.notifications.models import Notification, NotificationTemplate


security_logger = logging.getLogger('security')


def _log_auth_event(user, request, action, status_value='success', error_message=''):
    if not settings.AUDIT_LOG_ENABLED:
        return
    organization = getattr(user, 'organization', None)
    if not organization:
        return
    try:
        AuditLog.objects.create(
            organization=organization,
            user=user,
            action=action,
            entity_type='User',
            entity_id=str(user.id),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status=status_value,
            error_message=error_message or '',
        )
    except Exception as exc:
        security_logger.warning('Audit log write failed: %s', exc)


def _register_failed_login(user, request, reason):
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= settings.AUTH_MAX_FAILED_ATTEMPTS:
        user.locked_until = timezone.now() + timedelta(minutes=settings.AUTH_LOCKOUT_MINUTES)
        user.save(update_fields=['failed_login_attempts', 'locked_until'])
        _log_auth_event(user, request, 'login_locked', status_value='warning', error_message=reason)
        _notify_admins_of_lockout(user, request, reason)
    else:
        user.save(update_fields=['failed_login_attempts'])
        _log_auth_event(user, request, 'login_failed', status_value='failure', error_message=reason)


def _notify_admins_of_lockout(user, request, reason):
    if not settings.LOCKOUT_NOTIFY_ADMINS:
        return
    organization = getattr(user, 'organization', None)
    if not organization:
        return

    admins = User.objects.filter(
        Q(is_superuser=True) | Q(role='admin'),
        organization=organization,
        is_active=True,
    )
    if not admins.exists():
        return

    ip_address = request.META.get('REMOTE_ADDR')
    context = {
        'user_email': user.email,
        'reason': reason,
        'ip_address': ip_address,
        'lockout_minutes': settings.AUTH_LOCKOUT_MINUTES,
    }
    default_subject = 'Security alert: account locked'
    default_message = (
        f"User account locked: {user.email}\n"
        f"Reason: {reason}\n"
        f"IP: {ip_address}\n"
        f"Lockout duration: {settings.AUTH_LOCKOUT_MINUTES} minutes"
    )

    templates = NotificationTemplate.objects.filter(
        organization=organization,
        name='security_lockout',
        is_active=True,
    )
    in_app_template = templates.filter(channel='in_app').first()
    email_template = templates.filter(channel='email').first()

    def render_template(value, fallback):
        if not value:
            return fallback
        try:
            return value.format(**context)
        except Exception:
            return fallback

    for admin in admins:
        Notification.objects.create(
            organization=organization,
            recipient=admin,
            template=in_app_template,
            channel='in_app',
            subject=render_template(getattr(in_app_template, 'subject', ''), default_subject),
            message=render_template(getattr(in_app_template, 'body', ''), default_message),
            is_sent=True,
            sent_at=timezone.now(),
        )

    try:
        send_mail(
            subject=render_template(getattr(email_template, 'subject', ''), default_subject),
            message=render_template(getattr(email_template, 'body', ''), default_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin.email for admin in admins],
            fail_silently=True,
        )
    except Exception as exc:
        security_logger.warning('Admin lockout email failed: %s', exc)


def _is_token_stale(user, token):
    password_changed_at = getattr(user, 'password_changed_at', None)
    if not password_changed_at:
        return False

    if timezone.is_naive(password_changed_at):
        password_changed_at = timezone.make_aware(password_changed_at, dt_timezone.utc)

    issued_at = token.get('iat')
    if not issued_at:
        return True

    issued_at_dt = datetime.fromtimestamp(int(issued_at), tz=dt_timezone.utc)
    return issued_at_dt < password_changed_at


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


class LoginView(APIView):
    """
    Class-based login view with proper CORS support
    Handles both POST (login) and OPTIONS (CORS preflight) requests
    """
    permission_classes = [AllowAny]
    
    def options(self, request, *args, **kwargs):
        """Handle CORS preflight requests"""
        return Response(status=status.HTTP_200_OK)
    
    def post(self, request):
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
            security_logger.warning('Login failed for unknown user: %s', username)
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_locked():
            _log_auth_event(user, request, 'login_blocked', status_value='warning', error_message='Account locked')
            return Response({
                'error': 'Account is locked. Please try again later.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not user.check_password(password):
            _register_failed_login(user, request, 'Invalid password')
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'User account is inactive'
            }, status=status.HTTP_403_FORBIDDEN)

        if user.role in settings.MFA_REQUIRED_ROLES and not user.mfa_enabled:
            _log_auth_event(user, request, 'mfa_required', status_value='warning', error_message='MFA not enabled')
            return Response({
                'error': 'MFA is required for this role. Please enable MFA.'
            }, status=status.HTTP_403_FORBIDDEN)

        if user.mfa_enabled:
            totp_code = request.data.get('totp_code')
            if not totp_code:
                _log_auth_event(user, request, 'mfa_missing', status_value='failure', error_message='MFA code missing')
                return Response({
                    'error': 'MFA code is required.'
                }, status=status.HTTP_403_FORBIDDEN)
            if not user.mfa_secret:
                _log_auth_event(user, request, 'mfa_missing_secret', status_value='failure', error_message='MFA secret missing')
                return Response({
                    'error': 'MFA is not configured correctly.'
                }, status=status.HTTP_403_FORBIDDEN)
            import pyotp
            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(str(totp_code).strip()):
                _log_auth_event(user, request, 'mfa_invalid', status_value='failure', error_message='Invalid MFA code')
                return Response({
                    'error': 'Invalid MFA code.'
                }, status=status.HTTP_403_FORBIDDEN)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = timezone.now()
        user.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login'])
        _log_auth_event(user, request, 'login_success')
        
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


# Keep the old function-based view for backward compatibility (to be deprecated)
@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login(request):
    """
    Deprecated: Use LoginView instead
    Login endpoint - returns access and refresh tokens
    """
    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=username)
    except User.DoesNotExist:
        security_logger.warning('Login failed for unknown user: %s', username)
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    if user.is_locked():
        _log_auth_event(user, request, 'login_blocked', status_value='warning', error_message='Account locked')
        return Response({
            'error': 'Account is locked. Please try again later.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if not user.check_password(password):
        _register_failed_login(user, request, 'Invalid password')
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.is_active:
        return Response({
            'error': 'User account is inactive'
        }, status=status.HTTP_403_FORBIDDEN)

    if user.role in settings.MFA_REQUIRED_ROLES and not user.mfa_enabled:
        _log_auth_event(user, request, 'mfa_required', status_value='warning', error_message='MFA not enabled')
        return Response({
            'error': 'MFA is required for this role. Please enable MFA.'
        }, status=status.HTTP_403_FORBIDDEN)

    if user.mfa_enabled:
        totp_code = request.data.get('totp_code')
        if not totp_code:
            _log_auth_event(user, request, 'mfa_missing', status_value='failure', error_message='MFA code missing')
            return Response({
                'error': 'MFA code is required.'
            }, status=status.HTTP_403_FORBIDDEN)
        if not user.mfa_secret:
            _log_auth_event(user, request, 'mfa_missing_secret', status_value='failure', error_message='MFA secret missing')
            return Response({
                'error': 'MFA is not configured correctly.'
            }, status=status.HTTP_403_FORBIDDEN)
        import pyotp
        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(str(totp_code).strip()):
            _log_auth_event(user, request, 'mfa_invalid', status_value='failure', error_message='Invalid MFA code')
            return Response({
                'error': 'Invalid MFA code.'
            }, status=status.HTTP_403_FORBIDDEN)

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = timezone.now()
    user.save(update_fields=['failed_login_attempts', 'locked_until', 'last_login'])
    _log_auth_event(user, request, 'login_success')
    
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
        user_id = token.get('user_id')
        if not user_id:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if _is_token_stale(user, token):
            _log_auth_event(user, request, 'token_refresh_rejected', status_value='warning', error_message='Token stale')
            return Response({
                'error': 'Token is no longer valid. Please sign in again.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
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
        _log_auth_event(user, request, 'password_change_failed', status_value='failure', error_message='Old password invalid')
        return Response({
            'error': 'Old password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user=user)
    except Exception as exc:
        return Response({
            'error': str(exc)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.password_changed_at = timezone.now()
    user.save(update_fields=['password', 'password_changed_at'])
    _log_auth_event(user, request, 'password_changed')
    
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
            _log_auth_event(user, request, 'mfa_verify_failed', status_value='failure', error_message='Invalid TOTP')
            return Response({
                'error': 'Invalid TOTP code'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save MFA settings
        user.mfa_enabled = True
        user.mfa_method = 'totp'
        user.mfa_secret = pending_secret
        user.save()

        _log_auth_event(user, request, 'mfa_enabled')
        
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
        _log_auth_event(user, request, 'mfa_disable_failed', status_value='failure', error_message='Invalid password')
        return Response({
            'error': 'Invalid password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    user.mfa_enabled = False
    user.mfa_method = None
    user.mfa_secret = None
    user.save()

    _log_auth_event(user, request, 'mfa_disabled')
    
    return Response({
        'detail': 'MFA disabled successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile
    
    Returns:
        {
            "id": "uuid",
            "username": "user@example.com",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "role": "agent",
            "organization_id": "uuid",
            "organization_name": "Acme Corp",
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "mfa_enabled": false,
            "last_login": "2026-02-12T22:00:00Z",
            "created_at": "2026-01-01T00:00:00Z"
        }
    """
    user = request.user
    
    return Response({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'role': user.role,
        'organization_id': str(user.organization_id) if user.organization_id else None,
        'organization_name': user.organization.name if user.organization else None,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'mfa_enabled': user.mfa_enabled,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }, status=status.HTTP_200_OK)
