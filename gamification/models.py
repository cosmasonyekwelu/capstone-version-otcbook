from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class OPHistory(models.Model):
    ACTION_CHOICES = (
        ("trade_logged", "Trade Logged"),
        ("trade_bonus", "Fast Trade Bonus"),
        ("invite", "Invite Teammate"),
        ("badge_unlocked", "Badge Unlocked"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="op_events"
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    points = models.IntegerField()
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} | {self.action} | +{self.points} OP"


class Badge(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    requirement = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="earned_badges"
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")
        ordering = ["-unlocked_at"]

    def __str__(self):
        return f"{self.user} → {self.badge.name}"


class Notification(models.Model):
    TYPE_CHOICES = (
        ("points", "Points"),
        ("badge", "Badge"),
        ("system", "System"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_read(self):
        self.is_read = True
        self.save()
