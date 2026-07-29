"""Capture Transparensea screenshots with Playwright (preferred)."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[3] / "docs" / "transparensea" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:8501"

PAGES = [
    ("Overview", "overview.png"),
    ("Inputs", "inputs.png"),
    ("Recommendations", "recommendations.png"),
    ("Adoption", "adoption.png"),
    ("Impact", "impact.png"),
    ("Exceptions", "exceptions.png"),
    ("Insights & Actions", "insights-actions.png"),
    ("Improvement", "improvement.png"),
    ("Model Details", "model-details.png"),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(BASE, wait_until="domcontentloaded", timeout=60000)
        page.get_by_text("Transparensea", exact=False).first.wait_for(timeout=45000)
        time.sleep(4)
        for label, filename in PAGES:
            print(f"capturing {label}")
            btn = page.get_by_role("button", name=label, exact=True)
            if btn.count() == 0:
                btn = page.locator("label").filter(has_text=label).first
            else:
                btn = btn.first
            btn.click()
            # Wait for plotly canvases when present
            time.sleep(3.5)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.4)
            path = OUT / filename
            page.screenshot(path=str(path), full_page=True)
            print(f"  wrote {path} ({path.stat().st_size} bytes)")
        # Narrow iframe-like capture of overview
        page.set_viewport_size({"width": 980, "height": 800})
        page.get_by_role("button", name="Overview", exact=True).click()
        time.sleep(2.5)
        page.screenshot(path=str(OUT / "overview-iframe-width.png"), full_page=True)
        print("  wrote overview-iframe-width.png")
        browser.close()


if __name__ == "__main__":
    main()
