"""
Audit-log viewer. Administrators only (enforced by AdminRequiredMixin).
"""
from django.views.generic import ListView

from accounts.mixins import AdminRequiredMixin

from .models import AuditLog


class AuditLogListView(AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = "auditlog/log_list.html"
    context_object_name = "logs"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related("user")
        action = self.request.GET.get("action", "").strip()
        if action:
            qs = qs.filter(action=action)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["actions"] = AuditLog.Action.choices
        ctx["selected_action"] = self.request.GET.get("action", "")
        return ctx
