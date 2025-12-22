from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "trader",
        "desk_name",
        "asset_symbol",
        "amount",
        "status",
        "issued_at",
    )
    list_filter = ("status", "issued_at", "desk_name")
    search_fields = ("invoice_number", "trader__email",
                     "desk_name", "asset_symbol")
    readonly_fields = ("invoice_number", "issued_at", "pdf_url")

    def has_delete_permission(self, request, obj=None):
        return False
