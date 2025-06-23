# accounts/signals.py
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from django.db import transaction # Import transaction to ensure atomicity

import logging
logger = logging.getLogger(__name__)

'''
# This signal receiver `activate_user_after_email_confirmation` is being temporarily disabled.
# The logic for activating the user (setting `user.is_active = True`)
# and ensuring the email is marked as verified (setting `email_address.verified = True`)
# has been moved directly into the `redirect_confirm_email` view function
# in `accounts/views.py`.

# This change is a diagnostic and temporary measure to ensure user activation
# happens reliably during email confirmation, especially in environments
# where Django signal dispatching or `allauth`'s internal processes
# might be inconsistent or difficult to debug without direct server access.

@receiver(email_confirmed)
def activate_user_after_email_confirmation(request, email_address, **kwargs):
    # Ensure all operations are atomic within this signal
    with transaction.atomic():
        user = email_address.user
        logger.info(f"[Signal] 'email_confirmed' signal received for user: {user.email}")

        # Refresh user and email_address objects from DB to get their absolute current state
        # before any potential modifications by this signal handler.
        # This helps in accurate logging.
        user.refresh_from_db()
        email_address.refresh_from_db()

        logger.info(f"[Signal] User {user.email} initial 'is_active' status: {user.is_active}")
        logger.info(f"[Signal] Email address {email_address.email} initial 'verified' status: {email_address.verified}")
        
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
            logger.info(f"[Signal] User {user.email} 'is_active' set to True and saved.")
        else:
            logger.info(f"[Signal] User {user.email} was already active. No change made.")

        # Refresh email_address from DB again to get its latest 'verified' status
        # after allauth's internal processing (which happens *before* this signal)
        # and after our potential user.is_active update.
        email_address.refresh_from_db()
        logger.info(f"[Signal] Email address {email_address.email} 'verified' status after signal: {email_address.verified}")

        if not email_address.verified:
            logger.error(f"[Signal] WARNING: Email address {email_address.email} still not verified after email_confirmed signal. This indicates a deeper allauth issue or a timing problem.")
        else:
            logger.info(f"[Signal] Email address {email_address.email} is confirmed (verified=True).")
'''
