from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Desk

User = get_user_model()



class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    workspace = serializers.CharField(max_length=255)
    referral = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def validate_workspace(self, value):
        if Desk.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "A company with this name already exists.")
        return value

    def create(self, validated_data):
        # 1. Create Desk
        desk = Desk.objects.create(name=validated_data["workspace"])

        # 2. Create user as desk owner
        user = User.objects.create(
            full_name=validated_data["name"],
            email=validated_data["email"],
            role="desk_owner",
            desk=desk,
        )
        user.set_password(validated_data["password"])
        user.save()

        # 3. Issue tokens
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return {
            "user": user,
            "token": access,
            "refresh": str(refresh),
        }

    def to_representation(self, instance):
        user = instance["user"]
        return {
            "token": instance["token"],
            "refresh": instance["refresh"],
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "plan": user.plan,
                "desk": user.desk.name if user.desk else None,
            }
        }



class KYCSerializer(serializers.Serializer):
    id_card = serializers.ImageField()
    address = serializers.CharField(max_length=255)

    def save(self, desk):
        desk.id_card = self.validated_data["id_card"]
        desk.address = self.validated_data["address"]
        desk.kyc_status = "submitted"
        desk.save()
        return desk



class AddUserSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=[
        ("trader", "Trader"),
        ("analyst", "Analyst"),
        ("viewer", "Viewer"),
    ])

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists.")
        return value

    def create(self, validated_data, desk):
        import secrets
        temp_password = secrets.token_hex(4)  # 8-character temp password

        user = User.objects.create(
            full_name=validated_data["full_name"],
            email=validated_data["email"],
            role=validated_data["role"],
            desk=desk
        )
        user.set_password(temp_password)
        user.save()

        return user, temp_password
