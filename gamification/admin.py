from django.contrib import admin
from .models import OPHistory, Badge, UserBadge, Notification



@admin.register(OPHistory)
class OPHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "points",
        "created_at",
    )
    list_filter = (
        "action",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__full_name",
    )
    readonly_fields = (
        "user",
        "action",
        "points",
        "meta",
        "created_at",
    )
    ordering = ("-created_at",)
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "requirement",
    )
    search_fields = (
        "code",
        "name",
    )
    ordering = ("code",)
    list_per_page = 50



@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "badge",
        "unlocked_at",
    )
    list_filter = (
        "badge",
        "unlocked_at",
    )
    search_fields = (
        "user__email",
        "user__full_name",
        "badge__name",
    )
    readonly_fields = (
        "user",
        "badge",
        "unlocked_at",
    )
    ordering = ("-unlocked_at",)
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "type",
        "title",
        "is_read",
        "created_at",
    )
    list_filter = (
        "type",
        "is_read",
        "created_at",
    )
    search_fields = (
        "user__email",
        "user__full_name",
        "title",
    )
    readonly_fields = (
        "user",
        "type",
        "title",
        "message",
        "created_at",
    )
    ordering = ("-created_at",)
    list_per_page = 50

    actions = ["mark_selected_as_read"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Allow marking as read only
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Mark selected notifications as read")
    def mark_selected_as_read(self, request, queryset):
        queryset.update(is_read=True)
