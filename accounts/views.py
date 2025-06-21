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
from django.http import Http404

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

def confirm_email(request, key):
    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            confirmation.confirm(request)
            return redirect("https://papertigercinema.com/login")
    except Exception:
        pass
    raise Http404("Confirmation link invalid or expired.")
