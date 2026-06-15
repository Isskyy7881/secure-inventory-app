"""
Inventory CRUD views.

Access rules (RBAC):
- Any logged-in user  : view the list and item details (read-only).
- Administrators only  : create, update, delete items.

Every administrator write action is recorded in the audit log.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.mixins import AdminRequiredMixin
from auditlog.models import AuditLog
from auditlog.services import log_event

from .forms import ItemForm
from .models import Item


class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "inventory/item_list.html"
    context_object_name = "items"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            # ORM filter -> parameterised query (safe from SQL injection).
            qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = "inventory/item_detail.html"
    context_object_name = "item"


class ItemCreateView(AdminRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy("inventory:list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_event(
            self.request,
            user=self.request.user,
            action=AuditLog.Action.ITEM_CREATE,
            detail=f"Created item {self.object.sku}",
        )
        messages.success(self.request, "Item created.")
        return response


class ItemUpdateView(AdminRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy("inventory:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        log_event(
            self.request,
            user=self.request.user,
            action=AuditLog.Action.ITEM_UPDATE,
            detail=f"Updated item {self.object.sku}",
        )
        messages.success(self.request, "Item updated.")
        return response


class ItemDeleteView(AdminRequiredMixin, DeleteView):
    model = Item
    template_name = "inventory/item_confirm_delete.html"
    success_url = reverse_lazy("inventory:list")
    context_object_name = "item"

    def form_valid(self, form):
        sku = self.object.sku  # capture before the row is deleted
        response = super().form_valid(form)
        log_event(
            self.request,
            user=self.request.user,
            action=AuditLog.Action.ITEM_DELETE,
            detail=f"Deleted item {sku}",
        )
        messages.success(self.request, "Item deleted.")
        return response
