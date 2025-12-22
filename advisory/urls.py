from django.urls import path
from .views import AdvisoryChatView, QuickInsightsView

urlpatterns = [
    path("chat/", AdvisoryChatView.as_view()),
    path("quick-insights/", QuickInsightsView.as_view()),
]
