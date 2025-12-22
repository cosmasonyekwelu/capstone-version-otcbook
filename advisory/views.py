from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.db import models

from .services import AdvisoryAIService
from .models import TradeInsight, RiskScore
from gamification.models import OPHistory


class AdvisoryChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.AI_ADVISORY_ENABLED:
            return Response({"error": "AI advisory disabled"}, status=403)

        question = request.data.get("question")
        if not question:
            return Response({"error": "Question required"}, status=400)

        answer = AdvisoryAIService.ask(question)

        TradeInsight.objects.create(
            user=request.user,
            question=question,
            response=answer,
        )

        return Response({"answer": answer})

class QuickInsightsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        op_points = (
            OPHistory.objects
            .filter(user=request.user)
            .aggregate(total=models.Sum("points"))
            .get("total") or 0
        )

        if op_points < 100:
            risk_level = "high"
        elif op_points < 500:
            risk_level = "medium"
        else:
            risk_level = "low"

        return Response({
            "op_trend": op_points,
            "risk_alert": risk_level,
            "volatility_warning": "High volatility assets require smaller sizing",
        })