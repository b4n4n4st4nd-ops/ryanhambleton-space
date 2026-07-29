"""Capture Transparensea page screenshots via Selenium Edge/Chrome."""

from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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


def make_driver():
    for factory in (_edge, _chrome):
        try:
            return factory()
        except Exception as exc:  # noqa: BLE001
            print(f"driver failed: {exc}")
    raise RuntimeError("No browser driver available")


def _edge():
    opts = EdgeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-gpu")
    return webdriver.Edge(options=opts)


def _chrome():
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-gpu")
    return webdriver.Chrome(options=opts)


def click_nav(driver, label: str) -> None:
    wait = WebDriverWait(driver, 25)
    # Prefer pills buttons, fallback to radio labels
    xpaths = [
        f"//button[normalize-space()='{label}']",
        f"//label[.//p[normalize-space()='{label}']]",
        f"//p[normalize-space()='{label}']/ancestor::label[1]",
    ]
    last_err = None
    for xp in xpaths:
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            driver.execute_script("arguments[0].click();", el)
            time.sleep(2.8)
            return
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"Could not click nav '{label}': {last_err}")


def main() -> None:
    driver = make_driver()
    try:
        driver.set_window_size(1440, 900)
        driver.get(BASE)
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Transparensea')]"))
        )
        time.sleep(4)
        for label, filename in PAGES:
            print(f"capturing {label} -> {filename}")
            click_nav(driver, label)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            path = OUT / filename
            driver.save_screenshot(str(path))
            print(f"  wrote {path} ({path.stat().st_size} bytes)")
            # Extra scrolled shot for Overview / Adoption flagship charts
            if label in {"Overview", "Adoption", "Impact"}:
                driver.execute_script("window.scrollTo(0, Math.min(720, document.body.scrollHeight/2));")
                time.sleep(0.6)
                scroll_path = OUT / f"{filename.replace('.png', '')}-scroll.png"
                driver.save_screenshot(str(scroll_path))
                print(f"  wrote {scroll_path}")
        driver.set_window_size(980, 800)
        click_nav(driver, "Overview")
        path = OUT / "overview-iframe-width.png"
        driver.save_screenshot(str(path))
        print(f"  wrote {path}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
