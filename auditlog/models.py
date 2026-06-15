"""
Audit log model.

Stores security-relevant events: logins (success/failure), logout,
registration, profile changes, inventory changes and blocked access attempts.

Rule: this table must NEVER contain passwords, tokens or other secrets.
"""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login success"
        LOGIN_FAILED = "LOGIN_FAILED", "Login failed"
        LOGOUT = "LOGOUT", "Logout"
        REGISTER = "REGISTER", "Registration"
        PROFILE_UPDATE = "PROFILE_UPDATE", "Profile update"
        ITEM_CREATE = "ITEM_CREATE", "Item created"
        ITEM_UPDATE = "ITEM_UPDATE", "Item updated"
        ITEM_DELETE = "ITEM_DELETE", "Item deleted"
        ACCESS_DENIED = "ACCESS_DENIED", "Access denied"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    # For failed logins the account may not exist, so we store the typed name.
    username_attempted = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=30, choices=Action.choices)
    detail = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "audit log entry"
        verbose_name_plural = "audit log"

    def __str__(self):
        who = self.user or self.username_attempted or "anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {who} - {self.get_action_display()}"
