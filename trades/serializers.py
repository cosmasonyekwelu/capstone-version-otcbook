from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Trade, Asset, Desk

User = get_user_model()


# -----------------------------------------------------
# ASSET SERIALIZER
# -----------------------------------------------------
class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            "id",
            "symbol",
            "name",
            "is_active",
            "is_custom",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# -----------------------------------------------------
# DESK SERIALIZER
# -----------------------------------------------------
class DeskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desk
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


# -----------------------------------------------------
# TRADE SERIALIZER (CREATE + DETAIL)
# -----------------------------------------------------
class TradeSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
    desk_name = serializers.CharField(source="desk.name", read_only=True)
    trader_email = serializers.EmailField(
        source="trader.email", read_only=True)
    side_display = serializers.CharField(
        source="get_side_display", read_only=True)

    reference_value = serializers.SerializerMethodField()

    class Meta:
        model = Trade
        fields = [
            "id",
            "trader",
            "trader_email",
            "asset",
            "asset_symbol",
            "desk",
            "desk_name",
            "side",
            "side_display",
            "amount_crypto",
            "amount_ngn",
            "rate",
            "reference_value",
            "profit_loss",
            "trade_date",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "trader",
            "profit_loss",
            "created_at",
        ]

    # -----------------------------
    # DERIVED VALUES
    # -----------------------------
    def get_reference_value(self, obj):
        return (obj.amount_crypto * obj.rate).quantize(Decimal("0.01"))

    # -----------------------------
    # VALIDATION
    # -----------------------------
    def validate(self, data):
        """
        Ensure amounts and rate are consistent.
        """

        amount_crypto = data.get("amount_crypto")
        amount_ngn = data.get("amount_ngn")
        rate = data.get("rate")

        if amount_crypto <= 0:
            raise serializers.ValidationError(
                {"amount_crypto": "Crypto amount must be greater than zero."}
            )

        if amount_ngn <= 0:
            raise serializers.ValidationError(
                {"amount_ngn": "NGN amount must be greater than zero."}
            )

        if rate <= 0:
            raise serializers.ValidationError(
                {"rate": "Rate must be greater than zero."}
            )

        return data

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, validated_data):
        """
        Bind trade to authenticated user.
        """
        request = self.context.get("request")
        validated_data["trader"] = request.user
        return super().create(validated_data)


# -----------------------------------------------------
# TRADE LIST SERIALIZER (LIGHTWEIGHT)
# -----------------------------------------------------
class TradeListSerializer(serializers.ModelSerializer):
    asset_symbol = serializers.CharField(source="asset.symbol", read_only=True)
    desk_name = serializers.CharField(source="desk.name", read_only=True)

    class Meta:
        model = Trade
        fields = [
            "id",
            "asset_symbol",
            "desk_name",
            "side",
            "amount_crypto",
            "amount_ngn",
            "rate",
            "profit_loss",
            "trade_date",
        ]


# -----------------------------------------------------
# P&L SUMMARY SERIALIZER
# -----------------------------------------------------
class PnLSummarySerializer(serializers.Serializer):
    total_trades = serializers.IntegerField()
    total_profit_loss = serializers.DecimalField(
        max_digits=18, decimal_places=2
    )

    total_buy_volume = serializers.DecimalField(
        max_digits=18, decimal_places=2
    )
    total_sell_volume = serializers.DecimalField(
        max_digits=18, decimal_places=2
    )

    by_asset = serializers.ListField(child=serializers.DictField())
    by_desk = serializers.ListField(child=serializers.DictField())
    by_date = serializers.ListField(child=serializers.DictField())
