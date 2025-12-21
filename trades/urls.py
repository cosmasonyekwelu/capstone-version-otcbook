from django.urls import path
from .views import (
    TradeCreateView,
    TradeListView,
    TradeDetailView,
    TradePnLView,
    TradeExportCSVView,
)

urlpatterns = [
    path("create/", TradeCreateView.as_view(), name="trade-create"),
    path("list/", TradeListView.as_view(), name="trade-list"),
    path("<int:pk>/", TradeDetailView.as_view(), name="trade-detail"),
    path("pnl/", TradePnLView.as_view(), name="trade-pnl"),
    path("export/csv/", TradeExportCSVView.as_view(), name="trade-export-csv"),
]
