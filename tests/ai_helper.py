import os
import json
import random
from faker import Faker
from openai import OpenAI

# =================================================================
# 1. KUNCI JAWABAN DROPDOWN UI (Wajib disamakan persis dengan UI)
# =================================================================
VALID_COMPANY_TYPES = [
    "Importer/Exporter", "Consignor/Consignee", "Marketplace", "Retailer", 
    "Service Aggregator", "Third-Party Logistics (3PL) Provider", 
    "Holding Company", "Cooperative (Co-op)", "Franchisee/Franchisor", "Manufacturer"
]

# TODO: Sesuaikan daftar ini dengan opsi yang benar-benar ada di UI Anda!
VALID_INDUSTRY_TYPES = ["Technology", "Finance", "Healthcare", "Education", "Retail"] 
VALID_LANGUAGES = ["English", "Indonesian"]

# Untuk lokasi, kita kunci dalam satu paket agar AI/Faker tidak mencampuradukkan 
# provinsi dan kota yang tidak nyambung (mencegah dropdown kosong).
VALID_LOCATIONS = [
    {"country": "Indonesia", "state": "Jawa Barat", "city": "Bandung", "location": "Sumur Bandung", "postal": "40111"},
    {"country": "Malaysia", "state": "Selangor", "city": "Petaling Jaya", "location": "Damansara", "postal": "47400"},
    {"country": "Philippines", "state": "Metro Manila", "city": "Makati", "location": "Bel-Air", "postal": "1209"},
    {"country": "Cambodia", "state": "Phnom Penh", "city": "Phnom Penh", "location": "Daun Penh", "postal": "12200"}
]

def get_faker_fallback_data():
    """Deterministic fallback using Faker."""
    print("\n[INFO] API Key tidak ditemukan atau API gagal. Menggunakan Deterministic Fallback (Faker)...")
    
    fake = Faker('en_US')
    Faker.seed(42)
    random.seed(42) 
    
    loc = random.choice(VALID_LOCATIONS)
    
    return {
        "Input Company Name": fake.company(),
        "Input Email": fake.company_email(),
        "phone_country_code": loc["country"],
        "Input Phone": f"812{random.randint(1000000, 9999999)}",
        "Choose Industry Type": random.choice(VALID_INDUSTRY_TYPES), 
        "Choose Company Type": random.choice(VALID_COMPANY_TYPES), 
        "Choose Language": random.choice(VALID_LANGUAGES),        
        "Input Address": fake.street_address(),
        "Country": loc["country"],
        "Choose State": loc["state"],
        "Choose City": loc["city"],
        "Choose Location": loc["location"],
        "Choose Postal Code": loc["postal"]
    }

def generate_full_company_data():
    """Fungsi utama menggunakan AI dengan Guardrails ketat."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return get_faker_fallback_data()

    # 2. PROMPT DENGAN GUARDRAILS UNTUK SEMUA DROPDOWN
    prompt = f"""
    Kamu adalah asisten QA Automation. Hasilkan JSON data perusahaan dummy.
    
    ATURAN KRITIS UNTUK FIELD DROPDOWN (PILIH SALAH SATU YANG SESUAI):
    - "Choose Company Type" WAJIB dari: {json.dumps(VALID_COMPANY_TYPES)}
    - "Choose Industry Type" WAJIB dari: {json.dumps(VALID_INDUSTRY_TYPES)}
    - "Choose Language" WAJIB dari: {json.dumps(VALID_LANGUAGES)}
    
    ATURAN KRITIS UNTUK LOKASI (PILIH SATU PAKET LENGKAP):
    Kamu WAJIB memilih SATU set lokasi dari array berikut dan membaginya ke field yang sesuai:
    {json.dumps(VALID_LOCATIONS)}
    
    Format Key wajib:
    "Input Company Name", "Input Email", "phone_country_code", "Input Phone",
    "Choose Industry Type", "Choose Company Type", "Choose Language", "Input Address",
    "Country", "Choose State", "Choose City", "Choose Location", "Choose Postal Code"
    """

    try:
        client = OpenAI(api_key=api_key, timeout=5.0)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        print("\n[INFO] Berhasil menggunakan AI untuk generate data!")
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"\n[WARNING] Eksekusi API gagal ({e}). Beralih ke Fallback...")
        return get_faker_fallback_data()