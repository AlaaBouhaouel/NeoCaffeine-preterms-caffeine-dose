# Purpose: Production settings driven by Railway environment variables.

import os
from urllib.parse import urlparse

from .base import *


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_from_url(url: str) -> dict[str, str | int]:
    parsed = urlparse(url)
    engine_by_scheme = {
        "postgres": "django.db.backends.postgresql",
        "postgresql": "django.db.backends.postgresql",
    }
    engine = engine_by_scheme.get(parsed.scheme)
    if engine is None:
        raise ValueError("Unsupported DATABASE_URL scheme")
    return {
        "ENGINE": engine,
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "",
        "PASSWORD": parsed.password or "",
        "HOST": parsed.hostname or "",
        "PORT": parsed.port or "",
    }


SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = _to_bool(os.environ.get("DJANGO_DEBUG", "false"))
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()]
DATABASES = {"default": _database_from_url(os.environ["DATABASE_URL"])}
ACTIVE_SIMULATION_BACKEND = os.environ.get("ACTIVE_SIMULATION_BACKEND", "demo")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
