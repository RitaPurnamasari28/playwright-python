import os
import json
import random
from faker import Faker
from openai import OpenAI

# =================================================================
# KUNCI JAWABAN DROPDOWN UI 
# =================================================================
VALID_COMPANY_TYPES = [
    "Importer/Exporter", "Consignor/Consignee", "Marketplace", "Retailer", 
    "Service Aggregator", "Third-Party Logistics (3PL) Provider", 
    "Holding Company", "Cooperative (Co-op)", "Franchisee/Franchisor", "Manufacturer"
]

# Sesuaikan dengan opsi yang ada di UI eSuite Anda
VALID_INDUSTRY_TYPES = ["Technology", "Finance", "Healthcare", "Education", "Retail"] 
VALID_LANGUAGES = ["English", "Indonesian"]

# Skema dinamis: Indonesia pakai Province/District, negara lain pakai State/Location
VALID_LOCATIONS = [
    {
        "Country": "Indonesia", 
        "Choose Province": "Jawa Barat", 
        "Choose City": "Bandung", 
        "Choose District": "Sumur Bandung", 
        "Choose Sub District": "Babakan Ciamis", 
        "Choose Postal Code": "40111"
    },
    {
        "Country": "Malaysia", 
        "Choose State": "Selangor", 
        "Choose City": "Petaling Jaya", 
        "Choose Location": "Damansara", 
        "Choose Postal Code": "47400"
    },
    {
        "Country": "Philippines", 
        "Choose State": "Metro Manila", 
        "Choose City": "Makati", 
        "Choose Location": "Bel-Air", 
        "Choose Postal Code": "1209"
    }
]

def get_faker_fallback_data():
    """Deterministic fallback using Faker."""
    print("\n[INFO] API Key tidak ditemukan atau API gagal. Menggunakan Deterministic Fallback (Faker)...")
    
    fake = Faker('en_US')
    Faker.seed(42)
    random.seed(42) 
    
    # Pilih satu set lokasi
    loc = random.choice(VALID_LOCATIONS)
    
    # Buat data dasar
    base_data = {
        "Input Company Name": fake.company(),
        "Input Email": fake.company_email(),
        "phone_country_code": loc["Country"], # Menggunakan "Country" kapital agar cocok dengan dict
        "Input Phone": f"812{random.randint(1000000, 9999999)}",
        "Choose Industry Type": random.choice(VALID_INDUSTRY_TYPES), 
        "Choose Company Type": random.choice(VALID_COMPANY_TYPES), 
        "Choose Language": random.choice(VALID_LANGUAGES),        
        "Input Address": fake.street_address(),
    }
    
    # Gabungkan (merge) data lokasi dinamis ke dalam base_data
    base_data.update(loc)
    
    return base_data

def generate_full_company_data():
    """Fungsi utama menggunakan AI dengan Guardrails ketat."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return get_faker_fallback_data()

    prompt = f"""
    Kamu adalah asisten QA Automation. Hasilkan JSON data perusahaan dummy berformat flat dictionary.
    
    ATURAN KRITIS UNTUK FIELD DROPDOWN (PILIH SALAH SATU YANG SESUAI):
    - "Choose Company Type" WAJIB dari: {json.dumps(VALID_COMPANY_TYPES)}
    - "Choose Industry Type" WAJIB dari: {json.dumps(VALID_INDUSTRY_TYPES)}
    - "Choose Language" WAJIB dari: {json.dumps(VALID_LANGUAGES)}
    
    ATURAN KRITIS UNTUK LOKASI (DYNAMIC SCHEMA):
    Kamu WAJIB memilih SATU dictionary lokasi utuh dari array berikut, lalu menyalin SEMUA key dan value-nya langsung ke dalam JSON utamamu:
    {json.dumps(VALID_LOCATIONS)}
    
    Contoh Output jika memilih Indonesia:
    {{
        "Input Company Name": "PT Nusantara",
        "Input Email": "admin@nusantara.com",
        "phone_country_code": "Indonesia",
        "Input Phone": "8123456789",
        "Choose Industry Type": "Technology",
        "Choose Company Type": "Retailer",
        "Choose Language": "Indonesian",
        "Input Address": "Jl. Merdeka No 1",
        "Country": "Indonesia",
        "Choose Province": "Jawa Barat",
        "Choose City": "Bandung",
        "Choose District": "Sumur Bandung",
        "Choose Sub District": "Babakan Ciamis",
        "Choose Postal Code": "40111"
    }}
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