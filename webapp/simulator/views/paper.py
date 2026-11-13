# Purpose: Serves the proof of concept paper (NeoCaffeine.pdf at the repository root) at a short, stable URL for QR codes.

from django.conf import settings
from django.http import FileResponse, Http404, HttpRequest
from django.views.decorators.http import require_GET

PAPER_DOWNLOAD_NAME = "NeoCaffeine.pdf"


@require_GET
def paper_view(request: HttpRequest) -> FileResponse:
    """Return the paper PDF inline, so phones open it in their PDF viewer; 404 if the file is missing."""
    paper_path = settings.PAPER_PDF_PATH
    if not paper_path.is_file():
        raise Http404("Paper not found.")
    return FileResponse(paper_path.open("rb"), content_type="application/pdf", filename=PAPER_DOWNLOAD_NAME)
