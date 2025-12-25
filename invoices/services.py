from django.utils import timezone
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

from .models import Invoice
from trades.models import Trade
from common.storage.cloudinary import upload_private_file


def generate_invoice_number():
    year = timezone.now().year
    count = Invoice.objects.filter(issued_at__year=year).count() + 1
    return f"OTC-{year}-{str(count).zfill(6)}"


class InvoiceService:
    @staticmethod
    def create_invoice_from_trade(
        trade: Trade,
        client_email: str = "",
    ) -> Invoice:
        if hasattr(trade, "invoice"):
            raise ValueError("Invoice already exists for this trade.")

        invoice = Invoice.objects.create(
            invoice_number=generate_invoice_number(),
            trade=trade,
            trader=trade.trader,
            desk_name=trade.desk.name,
            asset_symbol=trade.asset.symbol,
            amount=trade.amount_ngn,
            client_email=client_email,
        )

        pdf_url = InvoiceService.generate_invoice_pdf(invoice)
        invoice.pdf_url = pdf_url
        invoice.save(update_fields=["pdf_url"])

        return invoice

    @staticmethod
    def generate_invoice_pdf(invoice: Invoice) -> str:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("INVOICE", styles["Title"]))
        elements.append(Spacer(1, 20))

        meta_table = Table([
            ["Invoice Number", invoice.invoice_number],
            ["Issued At", invoice.issued_at.strftime("%Y-%m-%d %H:%M")],
            ["Desk", invoice.desk_name],
            ["Asset", invoice.asset_symbol],
            ["Amount (NGN)", f"{invoice.amount:,.2f}"],
            ["Status", invoice.get_status_display()],
        ])

        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        if invoice.client_email:
            elements.append(
                Paragraph(
                    f"Billed To: {invoice.client_email}",
                    styles["Normal"],
                )
            )

        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        cloudinary_url = upload_private_file(
            file_obj=BytesIO(pdf_bytes),
            public_id=f"invoices/{invoice.invoice_number}",
        )

        return cloudinary_url
