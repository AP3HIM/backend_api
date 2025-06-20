from django.urls import path, include
from .views import (
    RegisterView,
    ProtectedView,
    user_profile,
    ResendConfirmationView,
)
from dj_rest_auth.registration.views import VerifyEmailView
from allauth.account.views import confirm_email


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('profile/', user_profile),
    path("resend-confirm/", ResendConfirmationView.as_view()),
    path('auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),  # ← ADD THIS
    path('auth/', include('dj_rest_auth.registration.urls')),  # <-- this is critical
    path("confirm-email/<key>/", confirm_email, name="account_confirm_email"),
]
