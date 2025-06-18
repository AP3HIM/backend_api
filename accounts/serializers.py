from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from allauth.account.utils import send_email_confirmation   # <-- add
from allauth.account.models import EmailAddress

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        validate_password(value)  # This runs all validators from settings
        return value

    def create(self, validated_data):
        user = User.objects.create_user(is_active=False, **validated_data)
        request = self.context.get("request")
        send_email_confirmation(request, user)
        return user
