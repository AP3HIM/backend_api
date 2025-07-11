# accounts/jwt.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class VerifiedEmailTokenSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that only issues tokens if the user's
    account is active (email confirmed and is_active=True).
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        if not user.is_active:
            raise serializers.ValidationError(
                "Your account is not active. Please confirm your email."
            )

        return data
