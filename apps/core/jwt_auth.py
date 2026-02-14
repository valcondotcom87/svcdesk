"""Custom JWT authentication helpers."""
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class PasswordChangedJWTAuthentication(JWTAuthentication):
    """Reject tokens issued before the last password change."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        password_changed_at = getattr(user, 'password_changed_at', None)
        if not password_changed_at:
            return user

        if timezone.is_naive(password_changed_at):
            password_changed_at = timezone.make_aware(password_changed_at, dt_timezone.utc)

        issued_at = validated_token.get('iat')
        if not issued_at:
            raise AuthenticationFailed('Token is missing issued-at claim.', code='token_not_valid')

        issued_at_dt = datetime.fromtimestamp(int(issued_at), tz=dt_timezone.utc)
        if issued_at_dt < password_changed_at:
            raise AuthenticationFailed('Token is no longer valid. Please sign in again.', code='token_not_valid')

        return user
