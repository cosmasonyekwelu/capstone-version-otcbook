from django.urls import path
from .views import (
    TradeCreateView,
    TradeListView,
    TradeDetailView,
    TradePnLView,
    TradeExportCSVView,
)

urlpatterns = [
    path("trades/create/", TradeCreateView.as_view(), name="trade-create"),
    path("trades/list/", TradeListView.as_view(), name="trade-list"),
    path("trades/<int:pk>/", TradeDetailView.as_view(), name="trade-detail"),
    path("trades/pnl/", TradePnLView.as_view(), name="trade-pnl"),
    path("trades/export/csv/", TradeExportCSVView.as_view(), name="trade-export-csv"),
]
