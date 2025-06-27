# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
import os # Add this import to use environment variables
from django.core.exceptions import ImproperlyConfigured

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False # Keep user inactive until email is confirmed
        if commit:
            user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        # IMPORTANT: Get your Django backend service's public URL from Render.
        # You *must* set a BACKEND_BASE_URL environment variable on Render for your backend service.
        # Example: If your backend is https://papertiger-backend.onrender.com,
        # this variable should be set to that exact URL.
        backend_base_url = os.environ.get("BACKEND_BASE_URL")
        if not backend_base_url:
            raise ImproperlyConfigured("Missing BACKEND_BASE_URL environment variable")

        # This constructs the URL to your custom Django view that handles confirmation.
        # It should align with your main urls.py (path('api/', include('accounts.urls')))
        # and accounts/urls.py (path('confirm-email/<key>/', redirect_confirm_email)).
        return f"{backend_base_url}/api/accounts/confirm-email/{emailconfirmation.key}/"
