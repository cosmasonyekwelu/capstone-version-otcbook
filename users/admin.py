from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, Desk


# -----------------------------------------------------
# DESK ADMIN SECTION
# -----------------------------------------------------
@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "kyc_status",
        "created_at",
        "kyc_document_link",
    )

    list_filter = ("kyc_status", "created_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "id_card_url", "kyc_document_link")

    fieldsets = (
        ("Desk Information", {
            "fields": ("name",)
        }),
        ("KYC Details", {
            "fields": (
                "id_card_url",
                "kyc_document_link",
                "kyc_status",
                "kyc_notes",
            )
        }),
        ("System Information", {
            "fields": ("created_at",)
        }),
    )

    def kyc_document_link(self, obj):
        if not obj.id_card_url:
            return "No document uploaded"
        return format_html(
            '<a href="{}" target="_blank">View ID Document</a>',
            obj.id_card_url,
        )

    kyc_document_link.short_description = "KYC Document"


# -----------------------------------------------------
# USER ADMIN SECTION
# -----------------------------------------------------
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "email",
        "full_name",
        "role",
        "desk",
        "plan",
        "is_active",
        "is_banned",
        "is_staff",
    )

    list_filter = (
        "role",
        "desk",
        "plan",
        "is_staff",
        "is_active",
        "is_banned",
    )

    search_fields = ("email", "full_name")
    ordering = ("email",)

    exclude = ("username",)

    fieldsets = (
        ("Login Credentials", {
            "fields": ("email", "password")
        }),
        ("Personal Information", {
            "fields": ("full_name", "phone")
        }),
        ("Role & Workspace", {
            "fields": ("role", "desk")
        }),
        ("Subscription Plan", {
            "fields": ("plan",)
        }),
        ("Platform Restrictions", {
            "fields": ("is_banned", "is_active")
        }),
        ("Admin Permissions", {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "phone",
                "role",
                "desk",
                "plan",
                "password1",
                "password2",
                "is_banned",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )


admin.site.register(User, UserAdmin)
