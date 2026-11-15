# Purpose: Checks that the landing page carries the three-card introduction as a hidden overlay with its own script, an Intro button, and a start button wired to the user guide.

from __future__ import annotations


def test_landing_page_has_hidden_intro_overlay(client) -> None:
    """The intro overlay is on the landing page after the landing stage, hidden until intro.js opens it."""
    html = client.get("/").content.decode()
    assert "simulator/css/intro.css" in html
    assert '<div id="intro-overlay" class="nc-intro-overlay" hidden>' in html
    assert html.index('id="landing-stage"') < html.index('id="intro-overlay"')
    assert html.count('class="nc-card nc-card--') == 3


def test_intro_script_loads_before_user_guide(client) -> None:
    """intro.js loads before user-guide.js, so the guide does not auto-open over the intro."""
    html = client.get("/").content.decode()
    assert html.index("simulator/js/intro.js") < html.index("simulator/js/user-guide.js")


def test_intro_has_open_button_and_start_link(client) -> None:
    """The form header has an Intro button and the intro's main link is marked to start the guide."""
    html = client.get("/").content.decode()
    assert 'class="intro-open-button"' in html
    assert 'href="#landing-stage" data-intro-start>' in html
