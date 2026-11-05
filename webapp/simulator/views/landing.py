# Purpose: Landing page handler for the NeoCaffeine web interface.

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def landing_view(request: HttpRequest) -> HttpResponse:
    return render(request, "landing.html")
