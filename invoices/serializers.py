from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    trade_id = serializers.IntegerField(
        source="trade.id",
        read_only=True,
    )

    trader_email = serializers.EmailField(
        source="trader.email",
        read_only=True,
    )

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "trade_id",
            "trader_email",
            "desk_name",
            "asset_symbol",
            "amount",
            "status",
            "pdf_url",
            "client_email",
            "issued_at",
        ]

        read_only_fields = [
            "id",
            "invoice_number",
            "trade_id",
            "trader_email",
            "desk_name",
            "asset_symbol",
            "amount",
            "status",
            "pdf_url",
            "issued_at",
        ]


class InvoiceCreateSerializer(serializers.Serializer):
    client_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
