"""
Account views: login, registration, dashboard and profile.

Login/logout reuse Django's built-in views (secure CSRF-protected flows).
Profile views always act on `request.user`, so a user can never read or edit
another user's profile (this prevents IDOR / insecure direct object reference).
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from auditlog.models import AuditLog
from auditlog.services import log_event

from .forms import ProfileUpdateForm, RegistrationForm


class UserLoginView(LoginView):
    """Custom-templated login. A successful login is logged via signals."""

    template_name = "registration/login.html"
    redirect_authenticated_user = True


def register(request):
    """Create a new account, then log the user in."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # password is hashed by UserCreationForm
            login(request, user)
            log_event(
                request,
                user=user,
                action=AuditLog.Action.REGISTER,
                detail="New account registered",
            )
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    """Landing page after login; links shown depend on the user's role."""
    return render(request, "dashboard.html")


class ProfileView(LoginRequiredMixin, DetailView):
    """Show the logged-in user's own profile."""

    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user  # always self -> no IDOR


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Edit the logged-in user's own profile."""

    form_class = ProfileUpdateForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user  # always self -> no IDOR

    def form_valid(self, form):
        response = super().form_valid(form)
        log_event(
            self.request,
            user=self.request.user,
            action=AuditLog.Action.PROFILE_UPDATE,
            detail="Profile updated",
        )
        messages.success(self.request, "Profile updated.")
        return response
