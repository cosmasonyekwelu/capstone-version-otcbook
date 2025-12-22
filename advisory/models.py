from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class RiskScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(help_text="0–100 risk score")
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class TradeInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    response = models.TextField()
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="low",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OPWeightedScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    op_points = models.IntegerField(default=0)
    trust_multiplier = models.DecimalField(max_digits=4, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
