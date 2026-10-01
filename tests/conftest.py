# conftest.py
import os
import sys
import json
import pytest
import allure
from playwright.sync_api import Page

# Ensure able to read file from othe folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import triage as triage


# Screenshot on failure fixture and attach to Allure report
@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(page: Page, request):
    yield
    # check if the test has failed
    if request.node.rep_call.failed:
        screenshot_bytes = page.screenshot(full_page=True)
        # attxh the screenshot to the allure report
        allure.attach(
            screenshot_bytes,
            name="screenshot_on_failure",
            attachment_type=allure.attachment_type.PNG,
        )


# check the status after running each test and store it
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # save the status of the test to the item for later use
    setattr(item, "rep_" + rep.when, rep)


# this hook is called after the whole test session finishes, we can use it to run the AI Triage and generate Allure environment and categories
@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    # 1. AI Triage
    print("\n\n suite done, running AI Triage...")
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
        {
            "name": "Locator & Timeout Errors",
            "traceRegex": ".*TimeoutError.*|.*Locator.*",
            "matchedStatuses": ["broken"],
        },
        {"name": "Assertion Failures", "matchedStatuses": ["failed"]},
        {"name": "Ignored Tests", "matchedStatuses": ["skipped"]},
    ]
    categories_path = os.path.join(allure_dir, "categories.json")
    with open(categories_path, "w") as f:
        json.dump(categories, f, indent=4)
