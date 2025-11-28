from django.urls import path
from .views import (
    SignupView,
    LoginView,
    upload_kyc,
    add_team_member,
    me
)

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),

    # Authenticated routes
    path("users/me/", me, name="me"),
    path("kyc/", upload_kyc, name="upload_kyc"),
    path("desk/add-trader/", add_team_member, name="add_team_member"),
]
