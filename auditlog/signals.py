"""
Signal handlers that turn Django auth events into audit-log entries.

Using the built-in signals means we catch logins/logouts no matter where they
happen (our views, the admin site, etc.).
"""
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

from .models import AuditLog
from .services import log_event


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_event(request, user=user, action=AuditLog.Action.LOGIN_SUCCESS,
              detail="User logged in")


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    log_event(request, user=user, action=AuditLog.Action.LOGOUT,
              detail="User logged out")


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request=None, **kwargs):
    # Django strips the password from `credentials` before sending the signal,
    # so only the (non-secret) username is recorded here.
    username = (credentials or {}).get("username", "")
    log_event(request, action=AuditLog.Action.LOGIN_FAILED,
              detail="Failed login attempt", success=False,
              username_attempted=username)
