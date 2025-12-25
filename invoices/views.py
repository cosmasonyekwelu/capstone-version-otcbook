from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
import requests

from .models import Invoice
from .serializers import InvoiceSerializer, InvoiceCreateSerializer
from .services import InvoiceService
from trades.models import Trade


# =====================================================
# CREATE INVOICE FROM TRADE
# POST /invoice/create/<trade_id>/
# =====================================================
class InvoiceCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceCreateSerializer

    def post(self, request, trade_id):
        trade = get_object_or_404(
            Trade,
            id=trade_id,
            trader=request.user,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoice = InvoiceService.create_invoice_from_trade(
            trade=trade,
            client_email=serializer.validated_data.get("client_email", ""),
        )

        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED,
        )


# =====================================================
# LIST USER INVOICES
# GET /invoice/list/
# =====================================================
class InvoiceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(trader=self.request.user)


# =====================================================
# DOWNLOAD INVOICE PDF (CLOUDINARY)
# GET /invoice/<id>/download/
# =====================================================
class InvoiceDownloadView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

    def get(self, request, *args, **kwargs):
        invoice = self.get_object()

        if invoice.trader != request.user:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not invoice.pdf_url:
            return Response(
                {"detail": "Invoice PDF not available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        resp = requests.get(invoice.pdf_url, stream=True)

        if resp.status_code != 200:
            return Response(
                {"detail": "Unable to retrieve invoice"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response = HttpResponse(
            resp.content,
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{invoice.invoice_number}.pdf"'
        )

        return response


# =====================================================
# SEND INVOICE TO CLIENT EMAIL
# POST /invoice/<id>/send/
# =====================================================
class InvoiceSendView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.all()

    def post(self, request, pk):
        invoice = get_object_or_404(
            Invoice,
            pk=pk,
            trader=request.user,
        )

        if not invoice.client_email:
            return Response(
                {"detail": "Client email not set for this invoice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not invoice.pdf_url:
            return Response(
                {"detail": "Invoice PDF not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resp = requests.get(invoice.pdf_url)

        if resp.status_code != 200:
            return Response(
                {"detail": "Unable to retrieve invoice PDF"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        email = EmailMessage(
            subject=f"Invoice {invoice.invoice_number}",
            body=(
                f"Dear Client,\n\n"
                f"Please find attached your invoice "
                f"{invoice.invoice_number}.\n\n"
                f"Thank you.\n\n"
                f"OTCBook"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.client_email],
        )

        email.attach(
            filename=f"{invoice.invoice_number}.pdf",
            content=resp.content,
            mimetype="application/pdf",
        )

        email.send(fail_silently=False)

        return Response(
            {"message": "Invoice sent successfully"},
            status=status.HTTP_200_OK,
        )
