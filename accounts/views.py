from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from rest_framework_simplejwt.views import TokenObtainPairView
from .jwt import VerifiedEmailTokenSerializer
from allauth.account.models import EmailConfirmationHMAC
from django.shortcuts import redirect
from django.http import HttpResponse

import logging
logger = logging.getLogger(__name__)


class ResendConfirmationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email", "").lower()
        try:
            user = EmailAddress.objects.get(email=email).user
            send_email_confirmation(request, user)
        except EmailAddress.DoesNotExist:
            pass
        return Response({"detail": "If that e-mail exists, a new confirmation link was sent."})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}. You're authenticated!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "id": user.id
    })

class VerifiedEmailTokenView(TokenObtainPairView):
    serializer_class = VerifiedEmailTokenSerializer

def redirect_confirm_email(request, key):
    logger.info(f"redirect_confirm_email: Attempting to confirm email with key: {key}")
    
    confirmation = EmailConfirmationHMAC.from_key(key)

    if confirmation:
        user = confirmation.email_address.user
        email_address = confirmation.email_address

        logger.info(f"redirect_confirm_email: Found confirmation for user: {user.username}, email: {email_address.email}")
        
        # --- START: Explicit Activation & Verification Logic ---
        # Refresh from DB to ensure we're working with the latest state before any updates
        user.refresh_from_db()
        email_address.refresh_from_db()
        logger.info(f"redirect_confirm_email: State BEFORE explicit update - User active: {user.is_active}, Email verified: {email_address.verified}")

        try:
            # Try allauth's confirmation method first. This might set `verified=True` and trigger signals.
            confirmation.confirm(request)
            logger.info(f"redirect_confirm_email: allauth's confirmation.confirm() called for {user.username}.")
        except Exception as e:
            # Log any error if allauth's confirm fails, but proceed to try manual activation
            logger.error(f"redirect_confirm_email: Error during allauth's confirmation.confirm() for {user.username}: {e}", exc_info=True)

        # Refresh from DB again to pick up any changes from allauth.confirm()
        user.refresh_from_db()
        email_address.refresh_from_db()

        # Explicitly set is_active and verified if they are not already True
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
            logger.info(f"redirect_confirm_email: User {user.username} explicitly activated (is_active=True).")
        else:
            logger.info(f"redirect_confirm_email: User {user.username} was already active. No change needed.")

        if not email_address.verified:
            email_address.verified = True
            email_address.save(update_fields=["verified"])
            logger.info(f"redirect_confirm_email: Email {email_address.email} explicitly marked as verified (verified=True).")
        else:
            logger.info(f"redirect_confirm_email: Email {email_address.email} was already verified. No change needed.")
        
        # Final state check after all operations for logging
        user.refresh_from_db()
        email_address.refresh_from_db()
        logger.info(f"redirect_confirm_email: Final state for {user.username}: is_active={user.is_active}, email_verified={email_address.verified}")
        # --- END: Explicit Activation & Verification Logic ---

    else:
        logger.warning(f"redirect_confirm_email: No valid email confirmation found for key: {key}. This link may be expired or invalid.")
        # Optional: Redirect to an invalid link page for a better user experience
        # return redirect("[https://papertigercinema.com/invalid-confirmation-link](https://papertigercinema.com/invalid-confirmation-link)") # Corrected URL here

    # Always redirect to login page after processing (or failing to process) confirmation
    return redirect("[https://papertigercinema.com/login](https://papertigercinema.com/login)") # Corrected URL here

