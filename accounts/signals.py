# accounts/signals.py
from allauth.account.signals import email_confirmed
from django.dispatch import receiver

@receiver(email_confirmed)
def activate_user_after_email_confirmation(request, email_address, **kwargs):
    user = email_address.user
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])
        print(f"[Signal] User {user.email} marked as active.")
