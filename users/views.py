from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    SignupSerializer,
    KYCSerializer,
    AddUserSerializer
)

User = get_user_model()


# =====================================================
# SIGNUP (Register Desk Owner)
# =====================================================
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"message": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = serializer.save()
        user = result["user"]

        return Response(
            {
                "token": result["token"],
                "refresh": result["refresh"],
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "plan": user.plan,
                    "desk": user.desk.name if user.desk else None,
                }
            },
            status=status.HTTP_201_CREATED
        )


# =====================================================
# LOGIN VIEW
# =====================================================
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"message": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"message": "Invalid email or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {"message": "Your account is deactivated. Contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        if getattr(user, "is_banned", False):
            return Response(
                {"message": "Your account has been banned by admin."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response(
            {
                "token": access,
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "plan": user.plan,
                    "desk": user.desk.name if user.desk else None,
                }
            },
            status=status.HTTP_200_OK
        )


# =====================================================
# GET LOGGED-IN USER /users/me/
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    return Response({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "plan": user.plan,
        "desk": user.desk.name if user.desk else None,
        "kyc_status": user.desk.kyc_status if user.desk else None,
    })


# =====================================================
# KYC UPLOAD (Desk Owner Only)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_kyc(request):
    user = request.user

    if user.role != "desk_owner":
        return Response({"message": "Only desk owners can submit KYC."}, status=403)

    if not user.desk:
        return Response({"message": "Desk not found."}, status=404)

    serializer = KYCSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user.desk)
        return Response({"message": "KYC submitted successfully."}, status=200)

    return Response(serializer.errors, status=400)


# =====================================================
# ADD TEAM MEMBER (Desk Owner Only)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_team_member(request):
    user = request.user

    if user.role != "desk_owner":
        return Response({"message": "Only desk owners can add team members."}, status=403)

    if not user.desk:
        return Response({"message": "Desk not found."}, status=404)

    serializer = AddUserSerializer(data=request.data)

    if serializer.is_valid():
        new_user, temp_password = serializer.create(serializer.validated_data, user.desk)

        return Response({
            "message": "Team member created successfully",
            "temporary_password": temp_password,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "desk": new_user.desk.name
            }
        })

    return Response(serializer.errors, status=400)
