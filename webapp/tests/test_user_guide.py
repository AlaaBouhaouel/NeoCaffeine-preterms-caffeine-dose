# Purpose: Proposal 07 checks: the landing page and the dashboard load the beginner guide and show its ? button.

from __future__ import annotations


def test_landing_page_loads_user_guide(client) -> None:
    """The landing page includes the guide script, its stylesheet and the ? button."""
    html = client.get("/").content.decode()
    assert "simulator/js/user-guide.js" in html
    assert "simulator/css/user-guide.css" in html
    assert 'class="guide-open-button"' in html


def test_dashboard_page_loads_user_guide(client, created_run) -> None:
    """The dashboard includes the guide script, its stylesheet and the ? button."""
    html = client.get(f"/runs/{created_run['run_id']}/").content.decode()
    assert "simulator/js/user-guide.js" in html
    assert "simulator/css/user-guide.css" in html
    assert 'id="guide-open-button"' in html
