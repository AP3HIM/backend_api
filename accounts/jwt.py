# accounts/jwt.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from allauth.account.models import EmailAddress

class VerifiedEmailTokenSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that only issues tokens if the user's
    email is verified and the account is active.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        email_verified = EmailAddress.objects.filter(
            user=user, verified=True, primary=True
        ).exists()

        if not email_verified or not user.is_active:
            raise serializers.ValidationError(
                "Your email is confirmed, but your account is not active."
                if email_verified else "E-mail address has not been confirmed."
            )

        return data
