# conftest.py
import os
import json
import pytest
import allure
from pydantic import BaseModel, ValidationError
from faker import Faker
from openai import OpenAI
import allure
from playwright.sync_api import Page
import os
import sys

# Mendaftarkan folder root proyek ke sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

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
    """Fallback deterministik menggunakan Faker"""
    return BusinessTestData(
        company=CompanyData(
            legal_name=fake.company(),
            email=fake.company_email(),
            phone=fake.phone_number(),
            street_address=fake.street_address(),
            industry=fake.job()
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

# Tambahkan import ini di bagian atas conftest.py
import triage as triage # Memanggil file triage.py yang sudah Anda buat

# Hook pytest yang berjalan setelah SEMUA test selesai
def pytest_sessionfinish(session, exitstatus):
    print("\n\n[INFO] Test suite selesai dieksekusi. Memulai AI Triage otomatis...")
    
    # Jalankan fungsi run_triage() dari file triage.py
    try:
        triage.run_triage()
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan AI Triage: {e}")

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