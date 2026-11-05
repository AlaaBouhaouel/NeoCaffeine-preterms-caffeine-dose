# Purpose: Root URL routing including health endpoint for deployment checks.

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthz(_request):
    return JsonResponse({"ok": True, "status": "healthy"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("", include("simulator.urls")),
]
