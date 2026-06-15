from django.apps import AppConfig


class AuditlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auditlog"
    verbose_name = "Audit Log & Monitoring"

    def ready(self):
        # Connect the login/logout/failed-login signal handlers.
        from . import signals  # noqa: F401
