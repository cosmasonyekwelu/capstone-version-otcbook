from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
import os

from .models import Invoice
from .serializers import InvoiceSerializer, InvoiceCreateSerializer
from .services import InvoiceService
from trades.models import Trade


class InvoiceCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceCreateSerializer

    def post(self, request, trade_id):
        trade = get_object_or_404(
            Trade,
            id=trade_id,
            trader=request.user
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = InvoiceService.create_invoice_from_trade(
            trade=trade,
            client_email=serializer.validated_data.get("client_email", "")
        )

        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED
        )


class InvoiceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(trader=self.request.user)


class InvoiceDownloadView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    def get(self, request, *args, **kwargs):
        invoice = self.get_object()

        if not invoice.pdf_url:
            return Response(
                {"detail": "Invoice PDF not available"},
                status=status.HTTP_404_NOT_FOUND
            )

        file_path = invoice.pdf_url.replace(
            settings.MEDIA_URL, settings.MEDIA_ROOT + "/")

        if not os.path.exists(file_path):
            return Response(
                {"detail": "Invoice file missing"},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            open(file_path, "rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=f"{invoice.invoice_number}.pdf"
        )


class InvoiceMarkPaidView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    def patch(self, request, *args, **kwargs):
        invoice = self.get_object()

        if invoice.trader != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        invoice.status = "paid"
        invoice.save(update_fields=["status"])

        return Response(InvoiceSerializer(invoice).data)
