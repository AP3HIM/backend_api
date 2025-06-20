# accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return True

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.is_active = False  # 👈 force inactive until email confirmed
        if commit:
            user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        # This replaces the default backend URL with your real frontend domain
        return f"https://papertigercinema.com/accounts/confirm-email/{emailconfirmation.key}/"
