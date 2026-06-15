"""
Helper functions for writing audit-log entries.

Keeping this in one place means every part of the app logs events the same
way, and the "no secrets in logs" rule is enforced here.
"""
from .models import AuditLog


def get_client_ip(request):
    """Best-effort client IP, honouring a single proxy hop if present."""
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_event(
    request=None,
    *,
    user=None,
    action,
    detail="",
    success=True,
    username_attempted="",
):
    """
    Create one AuditLog row.

    Only safe, non-sensitive fields are stored. Callers must never pass a
    password or token in `detail`.
    """
    user_agent = ""
    if request is not None:
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]

    # Resolve a real, saved user (AnonymousUser -> None).
    safe_user = user if (user is not None and getattr(user, "is_authenticated", False)) else None

    return AuditLog.objects.create(
        user=safe_user,
        username_attempted=(username_attempted or "")[:150],
        action=action,
        detail=(detail or "")[:255],
        ip_address=get_client_ip(request),
        user_agent=user_agent,
        success=success,
    )
