# Purpose: Proposal 08 checks: both pages load the phone stylesheet last, and the dashboard's phone-only details button starts hidden.

from __future__ import annotations

import re


def stylesheet_links(html: str) -> list[str]:
    """Return the href of every stylesheet link, in page order."""
    return re.findall(r'<link rel="stylesheet" href="([^"]+)"', html)


def test_landing_page_loads_phone_stylesheet_last(client) -> None:
    """The landing page links mobile.css after every other stylesheet."""
    links = stylesheet_links(client.get("/").content.decode())
    assert links[-1].endswith("simulator/css/mobile.css")


def test_dashboard_loads_phone_stylesheet_and_hidden_details_button(client, created_run) -> None:
    """The dashboard links mobile.css last and ships the details button hidden for large screens."""
    html = client.get(f"/runs/{created_run['run_id']}/").content.decode()
    assert stylesheet_links(html)[-1].endswith("simulator/css/mobile.css")
    assert 'aria-controls="dashboard-sidebar" hidden>' in html
