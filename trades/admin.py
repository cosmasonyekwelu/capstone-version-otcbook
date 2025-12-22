from django.contrib import admin
from .models import Trade, Asset


# Register your models here.
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "symbol",
        "name",
        "is_active",
        "is_custom",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_custom",
    )

    search_fields = (
        "symbol",
        "name",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("symbol",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "trade_date",
        "trader",
        "desk",
        "asset",
        "side",
        "trade_type",
        "amount_ngn",
        "profit_loss",
    )

    list_filter = (
        "side",
        "trade_type",
        "asset",
        "desk",
        "trade_date",
    )

    search_fields = (
        "trader__email",
        "asset__symbol",
        "desk__name",
    )

    date_hierarchy = "trade_date"

    readonly_fields = (
        "trader",
        "desk",
        "asset",
        "side",
        "trade_type",
        "amount_crypto",
        "amount_ngn",
        "rate",
        "profit_loss",
        "trade_date",
        "created_at",
    )

    ordering = ("-trade_date",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
