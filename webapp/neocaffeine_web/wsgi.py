# Purpose: WSGI application entrypoint for NeoCaffeine web deployments.

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "neocaffeine_web.settings.prod")

application = get_wsgi_application()
