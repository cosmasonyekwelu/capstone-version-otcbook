from django.urls import path
from .views import (
    InvoiceCreateView,
    InvoiceListView,
    InvoiceDownloadView,
    InvoiceSendView,
)

urlpatterns = [
    path("create/<int:trade_id>/", InvoiceCreateView.as_view()),
    path("list/", InvoiceListView.as_view()),
    path("<int:pk>/download/", InvoiceDownloadView.as_view()),
    path("<int:pk>/send/", InvoiceSendView.as_view()),
]
