# Purpose: Verifies the /paper URL serves the proof of concept PDF inline and returns 404 when the file is missing.

from __future__ import annotations


def test_paper_is_served_inline_as_pdf(client, settings, tmp_path) -> None:
    paper = tmp_path / "NeoCaffeine.pdf"
    paper.write_bytes(b"%PDF-1.7 test paper")
    settings.PAPER_PDF_PATH = paper
    for url in ("/paper", "/paper/"):
        response = client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert response["Content-Disposition"].startswith("inline")
        assert b"".join(response.streaming_content).startswith(b"%PDF")


def test_missing_paper_returns_404(client, settings, tmp_path) -> None:
    settings.PAPER_PDF_PATH = tmp_path / "missing.pdf"
    assert client.get("/paper").status_code == 404


def test_paper_rejects_post(client, settings, tmp_path) -> None:
    paper = tmp_path / "NeoCaffeine.pdf"
    paper.write_bytes(b"%PDF-1.7 test paper")
    settings.PAPER_PDF_PATH = paper
    assert client.post("/paper").status_code == 405


def test_default_paper_path_points_to_docs_poc(settings) -> None:
    assert settings.PAPER_PDF_PATH.name == "NeoCaffeine.pdf"
    assert settings.PAPER_PDF_PATH.parent.name == "poc"
    assert (settings.PAPER_PDF_PATH.parents[2] / "pyproject.toml").is_file()
    assert settings.PAPER_PDF_PATH.is_file()
