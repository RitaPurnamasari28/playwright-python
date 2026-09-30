import os
import json
import random
from faker import Faker
from openai import OpenAI

# 1. KUNCI JAWABAN DROPDOWN UI (Mencegah Playwright Timeout)
VALID_COMPANY_TYPES = [
    "Importer/Exporter", "Consignor/Consignee", "Marketplace", "Retailer", 
    "Service Aggregator", "Third-Party Logistics (3PL) Provider", 
    "Holding Company", "Cooperative (Co-op)", "Franchisee/Franchisor", "Manufacturer"
]

def get_faker_fallback_data():
    """Deterministic fallback using Faker."""
    print("\n[INFO] API Key tidak ditemukan atau API gagal. Menggunakan Deterministic Fallback (Faker)...")
    
    fake = Faker('en_US')
    Faker.seed(42)
    random.seed(42) 
    
    valid_locations = [
        {"country": "Indonesia", "state": "Jawa Barat", "city": "Bandung", "location": "Sumur Bandung", "postal": "40111"},
        {"country": "Malaysia", "state": "Selangor", "city": "Petaling Jaya", "location": "Damansara", "postal": "47400"},
        {"country": "Philippines", "state": "Metro Manila", "city": "Makati", "location": "Bel-Air", "postal": "1209"},
        {"country": "Cambodia", "state": "Phnom Penh", "city": "Phnom Penh", "location": "Daun Penh", "postal": "12200"}
    ]
    
    loc = random.choice(valid_locations)
    
    return {
        "Input Company Name": fake.company(),
        "Input Email": fake.company_email(),
        "phone_country_code": loc["country"],
        "Input Phone": f"812{random.randint(1000000, 9999999)}",
        "Choose Industry Type": "Technology", 
        "Choose Company Type": random.choice(VALID_COMPANY_TYPES), # <-- DIPERBAIKI! Tidak lagi hardcode "Private"
        "Choose Language": "English",        
        "Input Address": fake.street_address(),
        "Country": loc["country"],
        "Choose State": loc["state"],
        "Choose City": loc["city"],
        "Choose Location": loc["location"],
        "Choose Postal Code": loc["postal"]
    }

def generate_full_company_data():
    """
    Fungsi utama: Mengecek API Key terlebih dahulu.
    Jika tidak ada API Key, langsung masuk ke deterministic fallback (Faker).
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return get_faker_fallback_data()

    # 2. PROMPT DITAMBAHKAN ATURAN KRITIS
    prompt = f"""
    Kamu adalah asisten QA Automation. Hasilkan JSON data perusahaan dummy.
    Negara wajib dari: Cambodia, Indonesia, Malaysia, Philippines.
    
    ATURAN KRITIS UNTUK DROPDOWN:
    - Untuk "Choose Company Type", KAMU WAJIB memilih HANYA SATU dari daftar persis ini: {json.dumps(VALID_COMPANY_TYPES)}
    
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