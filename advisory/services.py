from groq import Groq
from django.conf import settings
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import RiskReport
from gamification.models import OPHistory


client = Groq(api_key=settings.GROQ_API_KEY)


# =====================================================
# EXISTING – DO NOT TOUCH
# =====================================================
class AdvisoryAIService:
    SYSTEM_PROMPT = """
You are a financial education assistant.
You provide general risk awareness, sizing concepts,
and performance interpretation for bookkeeping users.
Always include a disclaimer.
"""

    @staticmethod
    def ask(question: str):
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": AdvisoryAIService.SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.4,
        )

        return completion.choices[0].message.content


# =====================================================
# NEW – RISK REPORT SERVICE
# =====================================================
class RiskReportService:
    @staticmethod
    def generate(user):
        # 1. Aggregate OP points
        total_op = (
            OPHistory.objects
            .filter(user=user)
            .aggregate(total=models.Sum("points"))
            .get("total") or 0
        )

        if total_op < 100:
            risk_level = "HIGH RISK"
        elif total_op < 500:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"

        # 2. AI prompt (TEXT ONLY)
        prompt = (
            f"Generate a concise risk awareness summary for a trader with:\n"
            f"- OP score: {total_op}\n"
            f"- Risk level: {risk_level}\n\n"
            f"Focus on education, position sizing, and risk discipline."
        )

        ai_summary = AdvisoryAIService.ask(prompt)

        # 3. Persist report record
        report = RiskReport.objects.create(
            user=user,
            ai_summary=ai_summary,
            status="generating",
        )

        # 4. Generate PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        elements = [
            Paragraph("AI Risk Advisory Report", styles["Title"]),
            Spacer(1, 20),
            Paragraph(f"User: {user.email}", styles["Normal"]),
            Paragraph(f"OP Score: {total_op}", styles["Normal"]),
            Paragraph(f"Risk Level: {risk_level}", styles["Normal"]),
            Spacer(1, 20),
            Paragraph("AI Summary", styles["Heading2"]),
            Spacer(1, 10),
            Paragraph(ai_summary, styles["Normal"]),
        ]

        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        report.status = "ready"
        report.save(update_fields=["status"])

        return pdf_bytes
