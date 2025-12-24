from rest_framework import serializers
from django.db.models import Sum
from .models import OPHistory, Badge, UserBadge, Notification


class OPHistorySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = OPHistory
        fields = ["id", "action", "action_display", "points", "meta", "created_at"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["code", "name", "description", "requirement"]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer()

    class Meta:
        model = UserBadge
        fields = ["badge", "unlocked_at"]


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "type_display",
            "title",
            "message",
            "is_read",
            "created_at",
        ]


class OPOverviewSerializer(serializers.Serializer):
    total_op = serializers.IntegerField()
