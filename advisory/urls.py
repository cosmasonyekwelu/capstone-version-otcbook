from django.urls import path
from .views import (
    AdvisoryChatView,
    QuickInsightsView,
    OPAnalysisView,
    RiskReportPDFView,
)

urlpatterns = [
    path("chat/", AdvisoryChatView.as_view()),
    path("quick-insights/", QuickInsightsView.as_view()),
    path("op-analysis/", OPAnalysisView.as_view()),
    path("risk-report/", RiskReportPDFView.as_view()),
]
