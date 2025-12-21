from django.urls import path
from .views import OPView, BadgeView, LeaderboardView, NotificationView

urlpatterns = [
    path("op/", OPView.as_view()),
    path("badges/", BadgeView.as_view()),
    path("leaderboard/", LeaderboardView.as_view()),
    path("notifications/", NotificationView.as_view()),
]
