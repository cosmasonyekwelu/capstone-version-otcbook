from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.db import models

from drf_spectacular.utils import extend_schema, OpenApiExample

from .services import AdvisoryAIService
from .models import TradeInsight, RiskScore, RiskReport
from gamification.models import OPHistory

from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


class AdvisoryChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="AI Advisory Chat",
        description="Ask an AI-powered trading advisory question. Response is educational and risk-focused.",
        request=dict,
        responses={
            200: {"answer": "string"},
            400: {"error": "Question required"},
            403: {"error": "AI advisory disabled"},
        },
        examples=[
            OpenApiExample(
                "Ask Advisory Question",
                value={
                    "question": "How should I size my BTC/NGN trade during high volatility?"
                },
            )
        ],
        tags=["Advisory"],
    )
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

    @extend_schema(
        summary="Quick Risk Insights",
        description="Returns OP trend, inferred risk alert level, and a volatility warning.",
        responses={
            200: {
                "op_trend": "integer",
                "risk_alert": "string",
                "volatility_warning": "string",
            }
        },
        examples=[
            OpenApiExample(
                "Quick Insights Example",
                value={
                    "op_trend": 320,
                    "risk_alert": "medium",
                    "volatility_warning": "High volatility assets require smaller sizing",
                },
            )
        ],
        tags=["Advisory"],
    )
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


class OPAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="OP Trust Analysis",
        description="Analyzes OP score and returns trust level and advisory weight.",
        responses={
            200: {
                "op_score": "integer",
                "trust_level": "string",
                "advisory_weight": "number",
            }
        },
        examples=[
            OpenApiExample(
                "OP Analysis Example",
                value={
                    "op_score": 480,
                    "trust_level": "medium",
                    "advisory_weight": 0.7,
                },
            )
        ],
        tags=["Advisory"],
    )
    def post(self, request):
        total_op = (
            OPHistory.objects
            .filter(user=request.user)
            .aggregate(total=models.Sum("points"))
            .get("total") or 0
        )

        if total_op < 100:
            trust_level = "low"
            advisory_weight = 0.4
        elif total_op < 500:
            trust_level = "medium"
            advisory_weight = 0.7
        else:
            trust_level = "high"
            advisory_weight = 1.0

        return Response({
            "op_score": total_op,
            "trust_level": trust_level,
            "advisory_weight": advisory_weight,
        })


class RiskReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Generate Risk Report PDF",
        description="Generates an AI-powered risk advisory report and returns it as a PDF.",
        responses={200: {"content": {"application/pdf": {}}}},
        tags=["Advisory"],
    )
    def post(self, request):
        total_op = (
            OPHistory.objects
            .filter(user=request.user)
            .aggregate(total=models.Sum("points"))
            .get("total") or 0
        )

        if total_op < 100:
            risk_level = "HIGH RISK"
        elif total_op < 500:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"

        ai_prompt = (
            f"Generate a concise risk awareness summary for a trader with:\n"
            f"- OP score: {total_op}\n"
            f"- Risk level: {risk_level}\n\n"
            f"Focus on education, position sizing, and risk discipline."
        )

        ai_summary = AdvisoryAIService.ask(ai_prompt)

        report = RiskReport.objects.create(
            user=request.user,
            ai_summary=ai_summary,
            status="generating",
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("AI Risk Advisory Report", styles["Title"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"User: {request.user.email}", styles["Normal"]))
        elements.append(Paragraph(f"OP Score: {total_op}", styles["Normal"]))
        elements.append(Paragraph(f"Risk Level: {risk_level}", styles["Normal"]))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("AI Summary", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(ai_summary, styles["Normal"]))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        report.status = "ready"
        report.save(update_fields=["status"])

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="risk_report.pdf"'

        return response
