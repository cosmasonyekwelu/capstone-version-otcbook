from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import UploadedFile

from .models import Desk
from common.storage.cloudinary import upload_private_file

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
                "A user with this email already exists."
            )
        return value

    def validate_workspace(self, value):
        if Desk.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "A company with this name already exists."
            )
        return value

    def create(self, validated_data):
        desk = Desk.objects.create(
            name=validated_data["workspace"]
        )

        user = User.objects.create(
            full_name=validated_data["name"],
            email=validated_data["email"],
            role="desk_owner",
            desk=desk,
        )
        user.set_password(validated_data["password"])
        user.save()

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "token": str(refresh.access_token),
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



ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class KYCSerializer(serializers.Serializer):
    id_card = serializers.FileField()
    address = serializers.CharField(max_length=255)

    def validate_id_card(self, file: UploadedFile):
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Invalid file type. Only JPG, PNG, or PDF allowed."
            )

        if file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                "File size must not exceed 5MB."
            )

        return file

    def save(self, desk: Desk):
        file = self.validated_data["id_card"]

        cloudinary_url = upload_private_file(
            file_obj=file,
            public_id=f"kyc/desk_{desk.id}",
        )

        desk.id_card_url = cloudinary_url
        desk.address = self.validated_data["address"]
        desk.kyc_status = "submitted"
        desk.save(
            update_fields=[
                "id_card_url",
                "address",
                "kyc_status",
            ]
        )

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
                "A user with this email already exists."
            )
        return value

    def create(self, validated_data, desk):
        import secrets

        temp_password = secrets.token_hex(4)

        user = User.objects.create(
            full_name=validated_data["full_name"],
            email=validated_data["email"],
            role=validated_data["role"],
            desk=desk,
        )
        user.set_password(temp_password)
        user.save()

        return user, temp_password
