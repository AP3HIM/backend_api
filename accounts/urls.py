from django.urls import path, include
from .views import (
    RegisterView,
    ProtectedView,
    user_profile,
    ResendConfirmationView,
    redirect_confirm_email,
)
from dj_rest_auth.registration.views import VerifyEmailView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('profile/', user_profile),
    path("resend-confirm/", ResendConfirmationView.as_view()),
    path('auth/account-confirm-email/<key>/', redirect_confirm_email, name='account_confirm_email'),
    path('auth/', include('dj_rest_auth.registration.urls')),  # <-- this is critical
]
