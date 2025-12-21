from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import timedelta

from .models import Trade


class TradeFilter(filters.FilterSet):
    asset = filters.CharFilter(
        field_name="asset__symbol",
        lookup_expr="iexact"
    )

    side = filters.ChoiceFilter(
        choices=Trade.SIDE_CHOICES
    )

    trade_type = filters.ChoiceFilter(
        choices=Trade.TRADE_TYPE_CHOICES
    )

    start_date = filters.DateFilter(
        field_name="trade_date",
        lookup_expr="date__gte"
    )

    end_date = filters.DateFilter(
        field_name="trade_date",
        lookup_expr="date__lte"
    )

    date_preset = filters.ChoiceFilter(
        choices=[
            ("today", "Today"),
            ("week", "This Week"),
            ("month", "This Month"),
            ("year", "This Year"),
        ],
        method="filter_date_preset"
    )

    min_amount_ngn = filters.NumberFilter(
        field_name="amount_ngn",
        lookup_expr="gte"
    )

    max_amount_ngn = filters.NumberFilter(
        field_name="amount_ngn",
        lookup_expr="lte"
    )

    min_profit = filters.NumberFilter(
        field_name="profit_loss",
        lookup_expr="gte"
    )

    max_profit = filters.NumberFilter(
        field_name="profit_loss",
        lookup_expr="lte"
    )

    is_profitable = filters.BooleanFilter(
        method="filter_is_profitable"
    )

    class Meta:
        model = Trade
        fields = [
            "asset",
            "side",
            "trade_type",
            "start_date",
            "end_date",
            "date_preset",
            "min_amount_ngn",
            "max_amount_ngn",
            "min_profit",
            "max_profit",
            "is_profitable",
        ]

    def filter_is_profitable(self, queryset, name, value):
        if value is True:
            return queryset.filter(profit_loss__gt=0)
        if value is False:
            return queryset.filter(profit_loss__lte=0)
        return queryset

    def filter_date_preset(self, queryset, name, value):
        today = timezone.now().date()

        if value == "today":
            return queryset.filter(trade_date__date=today)

        if value == "week":
            start = today - timedelta(days=today.weekday())
            return queryset.filter(trade_date__date__gte=start)

        if value == "month":
            start = today.replace(day=1)
            return queryset.filter(trade_date__date__gte=start)

        if value == "year":
            start = today.replace(month=1, day=1)
            return queryset.filter(trade_date__date__gte=start)

        return queryset
