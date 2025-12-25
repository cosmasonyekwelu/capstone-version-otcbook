from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import OPHistory, UserBadge, Notification
from .serializers import (
    OPHistorySerializer,
    UserBadgeSerializer,
    NotificationSerializer,
)


class OPView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get OP Total",
        description="Returns the total OP (points) accumulated by the authenticated user.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_op": {"type": "integer"},
                },
            }
        },
        examples=[
            OpenApiExample(
                "OP Total Example",
                value={"total_op": 420},
            )
        ],
        tags=["Gamification"],
    )
    def get(self, request):
        total = (
            OPHistory.objects.filter(user=request.user)
            .aggregate(total=Sum("points"))["total"]
            or 0
        )
        return Response({"total_op": total})


class BadgeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get User Badges",
        description="Returns all badges earned by the authenticated user.",
        responses={200: UserBadgeSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Badge List Example",
                value=[
                    {
                        "id": 1,
                        "badge": {
                            "id": 1,
                            "name": "First Trade",
                            "description": "Completed first trade",
                        },
                        "earned_at": "2024-06-10T14:32:00Z",
                    }
                ],
            )
        ],
        tags=["Gamification"],
    )
    def get(self, request):
        badges = UserBadge.objects.filter(
            user=request.user).select_related("badge")
        return Response(UserBadgeSerializer(badges, many=True).data)


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Leaderboard",
        description="Returns the top 10 users ranked by total OP points.",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "user__email": {"type": "string"},
                        "total_op": {"type": "integer"},
                    },
                },
            }
        },
        examples=[
            OpenApiExample(
                "Leaderboard Example",
                value=[
                    {"user__email": "trader1@otcbook.com", "total_op": 920},
                    {"user__email": "trader2@otcbook.com", "total_op": 870},
                ],
            )
        ],
        tags=["Gamification"],
    )
    def get(self, request):
        data = (
            OPHistory.objects.values("user__email")
            .annotate(total_op=Sum("points"))
            .order_by("-total_op")[:10]
        )
        return Response(data)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Notifications",
        description="Returns all notifications for the authenticated user.",
        responses={200: NotificationSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Notification List Example",
                value=[
                    {
                        "id": 5,
                        "title": "New Badge Earned",
                        "message": "You earned the First Trade badge.",
                        "is_read": False,
                        "created_at": "2024-06-12T09:15:00Z",
                    }
                ],
            )
        ],
        tags=["Gamification"],
    )
    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(qs, many=True).data)
