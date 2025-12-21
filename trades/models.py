from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

User = settings.AUTH_USER_MODEL


# -----------------------------------------------------
# ASSET MODEL
# -----------------------------------------------------
class Asset(models.Model):
    """
    Asset registry for trade recording.

    - Seeded with major crypto assets
    - Supports custom / OTC-only assets
    - Never deletes historical trades
    """

    symbol = models.CharField(
        max_length=10,
        unique=True,
        help_text="Asset symbol (e.g. BTC, ETH, USDT)"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable asset name"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Inactive assets remain for historical records"
    )
    is_custom = models.BooleanField(
        default=False,
        help_text="True if asset was user-added (OTC / obscure asset)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["symbol"]
        verbose_name = "Asset"
        verbose_name_plural = "Assets"

    def __str__(self):
        return f"{self.symbol} - {self.name}"


# -----------------------------------------------------
# DESK MODEL
# -----------------------------------------------------
class Desk(models.Model):
    """
    Logical trading desk / book.

    Used for:
    - Reporting
    - Filtering
    - P&L aggregation
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Desk name (e.g. OTC Desk, P2P Desk)"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Desk"
        verbose_name_plural = "Desks"

    def __str__(self):
        return self.name


# -----------------------------------------------------
# TRADE MODEL
# -----------------------------------------------------
class Trade(models.Model):
    """
    Immutable trade ledger record.

    Represents a COMPLETED trade.
    No inventory simulation.
    No retroactive recalculation.
    """

    SIDE_CHOICES = (
        ("buy", "Buy"),
        ("sell", "Sell"),
    )

    trader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trades"
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name="trades"
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.PROTECT,
        related_name="trades"
    )

    side = models.CharField(
        max_length=4,
        choices=SIDE_CHOICES
    )

    amount_crypto = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
        help_text="Crypto amount traded"
    )

    amount_ngn = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Actual cash value of the trade (NGN)"
    )

    rate = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Reference rate (NGN per 1 unit of crypto)"
    )

    profit_loss = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        editable=False,
        default=Decimal("0.00"),
        help_text="Auto-calculated realized P&L (NGN)"
    )

    trade_date = models.DateTimeField(
        help_text="When the trade actually occurred"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-trade_date"]
        verbose_name = "Trade"
        verbose_name_plural = "Trades"
        indexes = [
            models.Index(fields=["trader", "trade_date"]),
            models.Index(fields=["asset", "trade_date"]),
            models.Index(fields=["desk", "trade_date"]),
        ]

    # -------------------------------------------------
    # P&L CALCULATION
    # -------------------------------------------------
    def calculate_pnl(self) -> Decimal:
        """
        Deterministic realized P&L.

        reference_value = amount_crypto * rate

        BUY  → profit = reference_value - amount_ngn
        SELL → profit = amount_ngn - reference_value
        """

        reference_value = self.amount_crypto * self.rate

        if self.side == "sell":
            pnl = self.amount_ngn - reference_value
        else:
            pnl = reference_value - self.amount_ngn

        return pnl.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # -------------------------------------------------
    # SAVE OVERRIDE
    # -------------------------------------------------
    def save(self, *args, **kwargs):
        # Enforce immutability
        if self.pk:
            raise ValueError("Trade records are immutable once created.")

        self.profit_loss = self.calculate_pnl()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.trader} | "
            f"{self.asset.symbol} | "
            f"{self.side.upper()} | "
            f"P&L: {self.profit_loss}"
        )
