# conftest.py
import os
import sys
import json
import pytest
import allure
from playwright.sync_api import Page
from pydantic import BaseModel, ValidationError
from faker import Faker
from openai import OpenAI
import random

# Mendaftarkan folder root proyek ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import module triage Anda
import triage as triage

# Inisialisasi Faker dengan locale Indonesia
fake = Faker('id_ID')
# Set seed agar deterministik saat fallback
Faker.seed(42)

# --- 1. Definisi Skema ---
class CompanyData(BaseModel):
    legal_name: str
    email: str
    phone: str
    street_address: str
    industry: str

class CustomerData(BaseModel):
    name: str
    contact: str
    address: str

class BusinessTestData(BaseModel):
    company: CompanyData
    customer: CustomerData

# --- 2. Modul Generator ---
def generate_fallback_data() -> BusinessTestData:

    valid_industries = [
        "Importer/Exporter", "Marketplace", "Retailer", 
        "Service Aggregator", "Holding Company"
    ]
    """Fallback deterministik menggunakan Faker"""
    return BusinessTestData(
        company=CompanyData(
            legal_name=fake.company(),
            email=fake.company_email(),
            phone=fake.phone_number(),
            street_address=fake.street_address(),
            industry=random.choice(valid_industries)
        ),
        customer=CustomerData(
            name=fake.name(),
            contact=fake.phone_number(),
            address=fake.address()
        )
    )

def generate_ai_business_data() -> BusinessTestData:
    api_key = os.getenv("OPENAI_API_KEY") # Guardrail: Key dari Environment Variable
    
    if not api_key:
        print("\n[INFO] No API Key found. Using deterministic Faker fallback.")
        return generate_fallback_data()

    client = OpenAI(api_key=api_key)
    
    prompt = """
    Generate coherent, realistic Indonesian business data.
    For the industry/company type field, YOU MUST strictly choose ONLY ONE from this exact list:
    ["Importer/Exporter", "Consignor/Consignee", "Marketplace", "Retailer", "Service Aggregator", "Third-Party Logistics (3PL) Provider", "Holding Company", "Cooperative (Co-op)", "Franchisee/Franchisor", "Manufacturer"]
    
    Output MUST be a valid JSON matching this schema exactly:
    {
        "company": {"legal_name": "", "email": "", "phone": "", "street_address": "", "industry": ""},
        "customer": {"name": "", "contact": "", "address": ""}
    }
    """
    
    try:
        # Gunakan model yang lebih murah (gpt-3.5-turbo atau gpt-4o-mini) untuk hemat token
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=300
        )
        
        raw_json = response.choices[0].message.content
        
        # Validasi skema (Reject & Retry / Fallback if malformed)
        return BusinessTestData.model_validate_json(raw_json)
        
    except (ValidationError, Exception) as e:
        print(f"\n[WARN] AI generation failed or malformed ({e}). Falling back to Faker.")
        return generate_fallback_data()

# --- 3. Pytest Fixture ---
@pytest.fixture
def business_data():
    """Fixture untuk diinjeksi ke test case dan di-attach ke Allure"""
    data = generate_ai_business_data()
    
    # Attach data yang BENAR-BENAR digunakan ke Allure Report
    allure.attach(
        body=data.model_dump_json(indent=2),
        name="AI_or_Fallback_Generated_Data.json",
        attachment_type=allure.attachment_type.JSON
    )
    return data

@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(page: Page, request):
    # Jalankan test case
    yield

    # Cek apakah test case mengalami kegagalan (failed)
    if request.node.rep_call.failed:
        # Ambil screenshot dalam bentuk bytes (tidak perlu disimpan ke folder lokal)
        screenshot_bytes = page.screenshot(full_page=True)

        # Lampirkan ke Allure Report
        allure.attach(
            screenshot_bytes,
            name="screenshot_on_failure",
            attachment_type=allure.attachment_type.PNG,
        )

# Hook tambahan untuk mendeteksi status test (passed/failed) di pytest
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# ==========================================
# GABUNGAN HOOK SESSION FINISH (Triage & Allure)
# ==========================================
@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    # 1. LOGIKA AI TRIAGE
    print("\n\n[INFO] Test suite selesai dieksekusi. Memulai AI Triage otomatis...")
    try:
        triage.run_triage()
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan AI Triage: {e}")

    # 2. LOGIKA ALLURE ENVIRONMENT & CATEGORIES
    # Pastikan nama folder ini sesuai dengan output allure Anda
    allure_dir = "allure-results"
    
    if not os.path.exists(allure_dir):
        os.makedirs(allure_dir)

    # 2a. Membuat file environment.properties
    env_content = """
    Browser=Chromium
    Environment=Staging
    Framework=Pytest-Playwright
    Tester=QA Engineer
    """
    env_path = os.path.join(allure_dir, "environment.properties")
    with open(env_path, "w") as f:
        f.write(env_content.strip())

    # 2b. Membuat file categories.json
    categories = [
        {
            "name": "Locator & Timeout Errors",
            "traceRegex": ".*TimeoutError.*|.*Locator.*",
            "matchedStatuses": ["broken"]
        },
        {
            "name": "Assertion Failures",
            "matchedStatuses": ["failed"]
        },
        {
            "name": "Ignored Tests",
            "matchedStatuses": ["skipped"]
        }
    ]
    categories_path = os.path.join(allure_dir, "categories.json")
    with open(categories_path, "w") as f:
        json.dump(categories, f, indent=4)