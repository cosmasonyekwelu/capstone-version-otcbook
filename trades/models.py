from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from users.models import Desk

User = settings.AUTH_USER_MODEL


class Asset(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_custom = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["symbol"]

    def __str__(self):
        return self.symbol


class Trade(models.Model):
    SIDE_CHOICES = (
        ("buy", "Buy"),
        ("sell", "Sell"),
    )

    TRADE_TYPE_CHOICES = (
        ("spot", "Spot"),
        ("otc", "OTC"),
        ("p2p", "P2P"),
        ("futures", "Futures"),
    )

    trader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trades",
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.PROTECT,
        related_name="trades",
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="trades",
    )

    side = models.CharField(
        max_length=4,
        choices=SIDE_CHOICES,
    )

    trade_type = models.CharField(
        max_length=10,
        choices=TRADE_TYPE_CHOICES,
    )

    amount_crypto = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )

    amount_ngn = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    rate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    profit_loss = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        editable=False,
    )

    trade_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-trade_date"]

    def calculate_pnl(self):
        reference_value = self.amount_crypto * self.rate
        pnl = (
            self.amount_ngn - reference_value
            if self.side == "sell"
            else reference_value - self.amount_ngn
        )
        return pnl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        self.profit_loss = self.calculate_pnl()
        super().save(*args, **kwargs)
