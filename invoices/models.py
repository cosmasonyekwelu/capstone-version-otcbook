from django.db import models
from django.conf import settings
from trades.models import Trade

User = settings.AUTH_USER_MODEL


class Invoice(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    )

    invoice_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    trade = models.OneToOneField(
        Trade,
        on_delete=models.PROTECT,
        related_name="invoice"
    )

    trader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="invoices"
    )

    desk_name = models.CharField(
        max_length=255,
        help_text="Snapshot of desk name at invoice time"
    )

    asset_symbol = models.CharField(
        max_length=10
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )

    pdf_url = models.URLField(blank=True)

    client_email = models.EmailField(blank=True)

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return self.invoice_number
