from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from .models import OPHistory, UserBadge, Notification
from .serializers import (
    OPHistorySerializer,
    UserBadgeSerializer,
    NotificationSerializer,
)


class OPView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = (
            OPHistory.objects.filter(user=request.user)
            .aggregate(total=Sum("points"))["total"]
            or 0
        )
        return Response({"total_op": total})


class BadgeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        badges = UserBadge.objects.filter(user=request.user).select_related("badge")
        return Response(UserBadgeSerializer(badges, many=True).data)


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            OPHistory.objects.values("user__email")
            .annotate(total_op=Sum("points"))
            .order_by("-total_op")[:10]
        )
        return Response(data)


class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)
        return Response(NotificationSerializer(qs, many=True).data)
