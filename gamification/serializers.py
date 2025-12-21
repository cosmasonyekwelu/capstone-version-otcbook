from rest_framework import serializers
from .models import OPHistory, Badge, UserBadge, Notification


class OPHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OPHistory
        fields = ["action", "points", "meta", "created_at"]


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["code", "name", "requirement"]


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer()

    class Meta:
        model = UserBadge
        fields = ["badge", "unlocked_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "type", "title", "message", "is_read", "created_at"]
