# conftest.py
import os
import sys
import json
import pytest
import allure
from playwright.sync_api import Page

# Mendaftarkan folder root proyek ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import triage as triage

# ==========================================
# PYTEST FIXTURES & HOOKS
# ==========================================
@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(page: Page, request):
    yield
    # Cek apakah test case mengalami kegagalan (failed)
    if request.node.rep_call.failed:
        screenshot_bytes = page.screenshot(full_page=True)
        allure.attach(
            screenshot_bytes,
            name="screenshot_on_failure",
            attachment_type=allure.attachment_type.PNG,
        )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    # 1. AI Triage
    print("\n\n[INFO] Test suite selesai dieksekusi. Memulai AI Triage otomatis...")
    try:
        triage.run_triage()
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan AI Triage: {e}")

    # 2. Allure Environment & Categories
    allure_dir = "allure-results"
    if not os.path.exists(allure_dir):
        os.makedirs(allure_dir)

    env_content = """
    Browser=Chromium
    Environment=Staging
    Framework=Pytest-Playwright
    Tester=QA Engineer
    """
    env_path = os.path.join(allure_dir, "environment.properties")
    with open(env_path, "w") as f:
        f.write(env_content.strip())

    categories = [
        {"name": "Locator & Timeout Errors", "traceRegex": ".*TimeoutError.*|.*Locator.*", "matchedStatuses": ["broken"]},
        {"name": "Assertion Failures", "matchedStatuses": ["failed"]},
        {"name": "Ignored Tests", "matchedStatuses": ["skipped"]}
    ]
    categories_path = os.path.join(allure_dir, "categories.json")
    with open(categories_path, "w") as f:
        json.dump(categories, f, indent=4)