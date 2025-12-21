from rest_framework import generics, permissions, filters as drf_filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from decimal import Decimal
import csv

from .models import Trade
from .serializers import (
    TradeSerializer,
    TradeListSerializer,
    PnLSummarySerializer,
)
from .filters import TradeFilter


class TradeCreateView(generics.CreateAPIView):
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class TradeListView(generics.ListAPIView):
    serializer_class = TradeListSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        drf_filters.OrderingFilter,
    ]
    filterset_class = TradeFilter
    ordering_fields = [
        "trade_date",
        "amount_ngn",
        "profit_loss",
        "rate",
    ]
    ordering = ["-trade_date"]

    def get_queryset(self):
        return (
            Trade.objects
            .filter(trader=self.request.user)
            .select_related("asset", "desk")
        )


class TradeDetailView(generics.RetrieveAPIView):
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Trade.objects
            .filter(trader=self.request.user)
            .select_related("asset", "desk")
        )


class TradePnLView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trades = Trade.objects.filter(trader=request.user)

        aggregates = trades.aggregate(
            total_trades=Count("id"),
            total_profit_loss=Sum("profit_loss"),
            total_buy_volume=Sum("amount_ngn", filter=Q(side="buy")),
            total_sell_volume=Sum("amount_ngn", filter=Q(side="sell")),
        )

        for key in aggregates:
            if aggregates[key] is None:
                aggregates[key] = Decimal("0.00")

        by_asset = (
            trades.values("asset__symbol")
            .annotate(
                trades=Count("id"),
                profit_loss=Sum("profit_loss"),
            )
            .order_by("-profit_loss")
        )

        by_desk = (
            trades.values("desk__name")
            .annotate(
                trades=Count("id"),
                profit_loss=Sum("profit_loss"),
            )
            .order_by("-profit_loss")
        )

        by_date = (
            trades.values("trade_date__date")
            .annotate(
                trades=Count("id"),
                profit_loss=Sum("profit_loss"),
            )
            .order_by("trade_date__date")
        )

        payload = {
            "total_trades": aggregates["total_trades"],
            "total_profit_loss": aggregates["total_profit_loss"],
            "total_buy_volume": aggregates["total_buy_volume"],
            "total_sell_volume": aggregates["total_sell_volume"],
            "by_asset": list(by_asset),
            "by_desk": list(by_desk),
            "by_date": list(by_date),
        }

        return Response(PnLSummarySerializer(payload).data)


class TradeExportCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trades = (
            Trade.objects
            .filter(trader=request.user)
            .select_related("asset", "desk")
            .order_by("-trade_date")
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="trades.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Trade ID",
            "Trade Date",
            "Asset",
            "Desk",
            "Side",
            "Trade Type",
            "Crypto Amount",
            "NGN Amount",
            "Rate",
            "Profit/Loss",
        ])

        for trade in trades:
            writer.writerow([
                trade.id,
                trade.trade_date,
                trade.asset.symbol,
                trade.desk.name,
                trade.side.upper(),
                trade.trade_type,
                trade.amount_crypto,
                trade.amount_ngn,
                trade.rate,
                trade.profit_loss,
            ])

        return response
