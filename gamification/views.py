from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

from .models import OPHistory, UserBadge, Notification
from .serializers import (
    OPHistorySerializer,
    UserBadgeSerializer,
    NotificationSerializer,
)
from .services import get_total_op


class OPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "total_op": get_total_op(request.user),
            "recent_activity": OPHistorySerializer(
                OPHistory.objects.filter(user=request.user)[:10],
                many=True
            ).data
        })


class BadgeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user)
        return Response(UserBadgeSerializer(badges, many=True).data)


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = timezone.now() - timedelta(days=7)

        leaderboard = (
            OPHistory.objects
            .filter(created_at__gte=start)
            .values("user__email")
            .annotate(points=Sum("points"))
            .order_by("-points")[:10]
        )

        return Response(leaderboard)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(notifications, many=True).data)
