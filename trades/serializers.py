from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Trade, Asset

User = get_user_model()


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
        read_only_fields = fields


class TradeSerializer(serializers.ModelSerializer):
    asset = serializers.CharField(write_only=True)

    asset_symbol = serializers.CharField(
        source="asset.symbol",
        read_only=True,
    )
    desk_name = serializers.CharField(
        source="desk.name",
        read_only=True,
    )
    trader_email = serializers.EmailField(
        source="trader.email",
        read_only=True,
    )
    side_display = serializers.CharField(
        source="get_side_display",
        read_only=True,
    )
    trade_type_display = serializers.CharField(
        source="get_trade_type_display",
        read_only=True,
    )

    class Meta:
        model = Trade
        fields = [
            "id",
            "asset",
            "asset_symbol",
            "desk_name",
            "side",
            "side_display",
            "trade_type",
            "trade_type_display",
            "amount_crypto",
            "amount_ngn",
            "rate",
            "profit_loss",
            "trade_date",
            "created_at",
            "trader_email",
        ]
        read_only_fields = [
            "id",
            "profit_loss",
            "created_at",
            "asset_symbol",
            "desk_name",
            "trader_email",
            "side_display",
            "trade_type_display",
        ]

    def validate(self, data):
        for field in ("amount_crypto", "amount_ngn", "rate"):
            if field in data and data[field] <= 0:
                raise serializers.ValidationError(
                    {field: "Value must be greater than zero."}
                )
        return data

    def create(self, validated_data):
        request = self.context["request"]

        symbol = validated_data.pop("asset").upper().strip()

        if not request.user.desk:
            raise serializers.ValidationError(
                "User is not assigned to a desk."
            )

        asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={
                "name": symbol,
                "is_active": True,
                "is_custom": True,
            },
        )

        return Trade.objects.create(
            trader=request.user,
            desk=request.user.desk,
            asset=asset,
            **validated_data,
        )


class TradeListSerializer(serializers.ModelSerializer):
    asset = serializers.CharField(
        source="asset.symbol",
        read_only=True,
    )
    desk = serializers.CharField(
        source="desk.name",
        read_only=True,
    )

    class Meta:
        model = Trade
        fields = [
            "id",
            "trade_date",
            "asset",
            "desk",
            "side",
            "trade_type",
            "amount_crypto",
            "amount_ngn",
            "rate",
            "profit_loss",
        ]


class PnLSummarySerializer(serializers.Serializer):
    total_trades = serializers.IntegerField()
    total_profit_loss = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    total_buy_volume = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    total_sell_volume = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    by_asset = serializers.ListField(child=serializers.DictField())
    by_desk = serializers.ListField(child=serializers.DictField())
    by_date = serializers.ListField(child=serializers.DictField())
