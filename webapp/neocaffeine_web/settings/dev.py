# Purpose: Local development settings for NeoCaffeine web app.

from .base import *


DEBUG = True
ALLOWED_HOSTS = ["*"]
STORAGES = {
    **STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
