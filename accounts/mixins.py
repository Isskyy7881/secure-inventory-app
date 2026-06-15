"""
Reusable access-control mixins for class-based views.

These centralise RBAC so every protected view enforces it the same way
(no copy-pasted checks that might drift apart).
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from auditlog.models import AuditLog
from auditlog.services import log_event


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Allow only authenticated users whose role is ADMIN.

    Behaviour:
    - Not logged in      -> redirected to the login page.
    - Logged in, not admin -> 403 Forbidden (and the attempt is logged).
    """

    def test_func(self):
        return getattr(self.request.user, "is_admin", False)

    def handle_no_permission(self):
        # Authenticated but failed the role test -> record and block (403).
        if self.request.user.is_authenticated:
            log_event(
                self.request,
                user=self.request.user,
                action=AuditLog.Action.ACCESS_DENIED,
                detail=f"Blocked admin-only access to {self.request.path}",
                success=False,
            )
            raise PermissionDenied
        # Anonymous -> default behaviour (redirect to login).
        return super().handle_no_permission()
