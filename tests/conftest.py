# conftest.py
import os
import sys
import json
import random
import pytest
import allure
from playwright.sync_api import Page
from faker import Faker
from openai import OpenAI

# Mendaftarkan folder root proyek ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import triage as triage

# Inisialisasi Faker dengan locale Indonesia
fake = Faker('id_ID')
Faker.seed(42)

# ==========================================
# 1. MODUL GENERATOR (Diperbarui ke Flat Dict)
# ==========================================
def generate_full_company_data():
    """Menghasilkan data perusahaan berformat dictionary datar untuk loop form otonom"""
    
    # KUNCI JAWABAN DROPDOWN (Penting agar tidak timeout)
    valid_industries = [
        "Importer/Exporter", "Consignor/Consignee", "Marketplace", "Retailer", 
        "Service Aggregator", "Third-Party Logistics (3PL) Provider", 
        "Holding Company", "Cooperative (Co-op)", "Franchisee/Franchisor", "Manufacturer"
    ]
    valid_phone_codes = ["Indonesia", "Philippines", "Malaysia", "Cambodia"]
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Fallback jika API Key tidak ada
    if not api_key:
        print("\n[INFO] No API Key found. Using deterministic Faker fallback.")
        return {
            "Input Company Name": fake.company(),
            "Input Email": fake.company_email(),
            "phone_country_code": random.choice(valid_phone_codes),
            "Input Phone Number": fake.msisdn(),
            "Industry Type": random.choice(valid_industries),
            "Choose Language": "English",
            "Country": "Indonesia",
            "Input Street Address": fake.street_address()
        }

    client = OpenAI(api_key=api_key)
    
    # Prompt yang sudah dikunci ketat untuk dropdown
    prompt = f"""
    Generate coherent, realistic Indonesian business data.
    Output MUST be a valid JSON object formatted as a flat dictionary.
    
    CRITICAL RULES FOR DROPDOWN FIELDS:
    - For "Industry Type" (or company type), YOU MUST strictly choose ONLY ONE from this exact list: {json.dumps(valid_industries)}
    - For "phone_country_code", YOU MUST strictly choose ONLY ONE from: {json.dumps(valid_phone_codes)}
    - For "Choose Language", choose "English" or "Indonesian".
    - For "Country", use a valid country name like "Indonesia".
    
    Example expected output format:
    {{
        "Input Company Name": "PT Maju Bersama",
        "Input Email": "admin@majubersama.com",
        "phone_country_code": "Indonesia",
        "Input Phone Number": "81234567890",
        "Industry Type": "Marketplace",
        "Choose Language": "Indonesian",
        "Country": "Indonesia",
        "Input Street Address": "Jl. Sudirman No.1"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=300
        )
        
        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        
        # Attach data ke Allure untuk kemudahan debugging
        allure.attach(
            body=json.dumps(data, indent=2),
            name="Generated_Company_Data.json",
            attachment_type=allure.attachment_type.JSON
        )
        return data
        
    except Exception as e:
        print(f"\n[WARN] AI generation failed ({e}). Falling back to Faker.")
        return {
            "Input Company Name": fake.company(),
            "Input Email": fake.company_email(),
            "phone_country_code": "Indonesia",
            "Input Phone Number": fake.msisdn(),
            "Industry Type": "Marketplace",
            "Choose Language": "English",
            "Country": "Indonesia",
            "Input Street Address": fake.street_address()
        }


# ==========================================
# 2. PYTEST FIXTURES & HOOKS
# ==========================================
@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(page: Page, request):
    yield
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
    with open(os.path.join(allure_dir, "environment.properties"), "w") as f:
        f.write(env_content.strip())

    categories = [
        {"name": "Locator & Timeout Errors", "traceRegex": ".*TimeoutError.*|.*Locator.*", "matchedStatuses": ["broken"]},
        {"name": "Assertion Failures", "matchedStatuses": ["failed"]},
        {"name": "Ignored Tests", "matchedStatuses": ["skipped"]}
    ]
    with open(os.path.join(allure_dir, "categories.json"), "w") as f:
        json.dump(categories, f, indent=4)