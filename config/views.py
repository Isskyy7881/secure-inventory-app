"""
Project-level views: the public home page and the custom error handlers.

The error handlers render friendly templates instead of exposing internal
details (stack traces, file paths). They are only used when DEBUG=False.
"""
from django.shortcuts import render


def home(request):
    """Public landing page."""
    return render(request, "home.html")


def bad_request(request, exception=None):
    return render(request, "400.html", status=400)


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    # NOTE: the 500 template must not rely on context processors.
    return render(request, "500.html", status=500)
