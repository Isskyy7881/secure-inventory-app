"""
Django settings for the Secure Inventory web application.

MEMBER 1 (Core Developer) baseline configuration.
The goal here is "secure by default": every framework security feature that
can be switched on safely is switched on, and anything that depends on the
deployment environment is read from a .env file (never hard-coded).

Team note:
- Member 3 (Security Mitigator) extends these controls (for example a strict
  Content-Security-Policy, extra custom validators). See HANDOFF_TEAM.md.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ------------------------------------------------------------------
# Paths and environment loading
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from the .env file into the process environment.
load_dotenv(BASE_DIR / ".env")


def env_bool(key, default=False):
    """Read a boolean value from the environment ('True'/'1'/'yes' -> True)."""
    return os.getenv(key, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(key, default=""):
    """Read a comma-separated list from the environment into a Python list."""
    raw = os.getenv(key, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# ------------------------------------------------------------------
# Core security settings
# ------------------------------------------------------------------
# SECRET_KEY must come from the environment. The fallback only exists so the
# project can still boot if someone forgets the .env; it is clearly unsafe.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-CHANGE-ME-set-SECRET_KEY-in-.env")

# DEBUG must be False in production (no stack traces leaked to users).
DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")

# ------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # --- Service modules (modular monolith) ---
    "accounts",     # users, RBAC, authentication, profile
    "inventory",    # secure CRUD module
    "auditlog",     # security event logging + admin log viewer
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",      # security headers
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",          # CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # clickjacking
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # template auto-escaping is ON by default -> stops XSS
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------------------
# Database
#   Default: SQLite (simple for dev/demo).
#   Optional: set DB_ENGINE etc. in .env to use PostgreSQL.
#   Either way we ONLY use the ORM -> protects against SQL injection.
# ------------------------------------------------------------------
if os.getenv("DB_ENGINE"):
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE"),
            "NAME": os.getenv("DB_NAME", ""),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ------------------------------------------------------------------
# Authentication / RBAC
# ------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"   # custom user model with a role field
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "home"

# Password hashing: Argon2 first (OWASP-recommended), strong fallbacks after.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Strong password rules (server-side enforced).
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Internationalisation
# ------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kuala_Lumpur"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Static and media files
# ------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Uploaded files are kept in /media (served separately, not from the code root).
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# Session and cookie hardening
# ------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True          # JS cannot read the session cookie
SESSION_COOKIE_SAMESITE = "Lax"         # mitigates CSRF / cross-site sending
SESSION_COOKIE_AGE = int(os.getenv("SESSION_COOKIE_AGE", "1800"))  # 30-min timeout
SESSION_SAVE_EVERY_REQUEST = True       # sliding expiry -> real idle timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool("SESSION_EXPIRE_AT_BROWSER_CLOSE", True)

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# Secure cookies default to ON in production (DEBUG=False); overridable via .env.
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)

# ------------------------------------------------------------------
# HTTPS / security headers
#   SSL redirect + HSTS default to OFF so local runs don't break;
#   ENABLE them in .env for production (values shown in .env.example).
# ------------------------------------------------------------------
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True          # stops MIME sniffing
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"                     # no framing -> clickjacking defence

if env_bool("USE_PROXY_SSL_HEADER", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")

# ------------------------------------------------------------------
# Flash messages -> CSS classes used in templates
# ------------------------------------------------------------------
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.DEBUG: "secondary",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}

# ------------------------------------------------------------------
# Logging (general app log; security AUDIT events go to the AuditLog model)
#   Rule: never write passwords/tokens to logs.
# ------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "app.log",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}
