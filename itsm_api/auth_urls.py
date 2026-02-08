"""
Authentication API URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from itsm_api.auth import (
    login, logout, change_password, verify_token,
    enable_mfa, verify_mfa, disable_mfa, CustomTokenObtainPairView
)

urlpatterns = [
    # Token endpoints
    path('login/', login, name='token_obtain_pair'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_custom'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout, name='token_logout'),
    
    # User account endpoints
    path('change-password/', change_password, name='change_password'),
    path('verify-token/', verify_token, name='verify_token'),
    
    # MFA endpoints
    path('mfa/enable/', enable_mfa, name='mfa_enable'),
    path('mfa/verify/', verify_mfa, name='mfa_verify'),
    path('mfa/disable/', disable_mfa, name='mfa_disable'),
]
