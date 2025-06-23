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

import logging # Add this import
logger = logging.getLogger(__name__) # Initialize logger for this module



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

    def post(self, request, *args, **kwargs):
        username_or_email = request.data.get("username") or request.data.get("email")
        user = User.objects.filter(username=username_or_email).first()

        logger.info(f"[LOGIN DEBUG] Username or email: {username_or_email}")
        if user:
            logger.info(f"[LOGIN DEBUG] User found. is_active: {user.is_active}")
        else:
            logger.error(f"[LOGIN DEBUG] No user found for: {username_or_email}")

        return super().post(request, *args, **kwargs)


def redirect_confirm_email(request, key):
    confirmation = EmailConfirmationHMAC.from_key(key)
    if confirmation:
        confirmation.confirm(request)
         # Force user to be active right here
        user = confirmation.email_address.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
            logger.info(f"[View] Set user {user.email} as active from confirm view.")
    # Always redirect to login page after confirming
    return redirect("https://papertigercinema.com/login")
