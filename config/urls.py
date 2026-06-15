"""
Root URL configuration.

Routes are grouped by service module:
- accounts  -> auth, registration, profile, dashboard
- inventory -> the secure CRUD module
- auditlog  -> admin-only security log viewer
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", core_views.home, name="home"),
    path("", include("accounts.urls")),       # /login, /register, /profile, ...
    path("inventory/", include("inventory.urls")),
    path("audit/", include("auditlog.urls")),
]

# Serve uploaded media during local development only.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (used when DEBUG=False) -> no stack traces to users.
handler400 = "config.views.bad_request"
handler403 = "config.views.permission_denied"
handler404 = "config.views.page_not_found"
handler500 = "config.views.server_error"
