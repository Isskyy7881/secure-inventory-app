from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "user", "username_attempted",
                    "ip_address", "success")
    list_filter = ("action", "success")
    search_fields = ("username_attempted", "detail", "ip_address")
    readonly_fields = ("user", "username_attempted", "action", "detail",
                       "ip_address", "user_agent", "success", "timestamp")

    def has_add_permission(self, request):
        return False  # audit entries are created by the app, never by hand

    def has_change_permission(self, request, obj=None):
        return False  # immutable from the admin UI
