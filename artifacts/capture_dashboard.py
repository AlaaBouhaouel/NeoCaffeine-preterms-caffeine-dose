import json
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

base = "http://127.0.0.1:8010"
payload = {
    "patient": {
        "sex": "male",
        "gestational_age_weeks": 28,
        "gestational_age_days_extra": 0,
        "birth_weight_g": 980,
    },
    "initial_context": {
        "fiO2_fraction": 0.3,
        "breathing_support": "room_air",
        "monitoring_on": True,
    }
}
req = urllib.request.Request(
    f"{base}/api/v1/runs",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=20) as resp:
    body = json.loads(resp.read().decode("utf-8"))
run_id = body["run_id"]
url = f"{base}/runs/{run_id}/"
Path("artifacts").mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    page.goto(url, wait_until="networkidle")
    page.screenshot(path="artifacts/dashboard_v3_1280x720.png", full_page=False)
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.goto(url, wait_until="networkidle")
    page.screenshot(path="artifacts/dashboard_v3_1920x1080.png", full_page=False)
    browser.close()
print("done", run_id)
