from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import Manager


# -----------------------------------------------------
# DESK MODEL (Workspace / Company)
# -----------------------------------------------------
class Desk(models.Model):
    name = models.CharField(max_length=255, unique=True)

    # Desk KYC details
    id_card = models.ImageField(upload_to="kyc/", null=True, blank=True)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    kyc_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -----------------------------------------------------
# USER MODEL for OTCBook
# -----------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ("desk_owner", "Desk Owner"),
        ("manager", "Manager"),
        ("trader", "Trader"),
        ("analyst", "Analyst"),
        ("viewer", "Viewer"),
        ("auditor", "Auditor"),
    )

    PLAN_CHOICES = (
        ("free", "Free Plan"),
        ("starter", "Starter Plan"),
        ("pro", "Pro Plan"),
        ("enterprise", "Enterprise Plan"),
    )

    # Remove username field
    username = None
    email = models.EmailField(unique=True)

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")

    desk = models.ForeignKey(
        Desk,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    is_banned = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = Manager()

    def __str__(self):
        return f"{self.full_name} <{self.email}> [{self.role}]"
