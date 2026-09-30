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
    {
        # Format Indonesia
        "Country": "Indonesia", 
        "Choose Province": "Jawa Barat", 
        "Choose City": "Bandung", 
        "Choose District": "Sumur Bandung", 
        "Choose Sub District": "Babakan Ciamis", 
        "Choose Postal Code": "40111"
    },
    {
        # Format Negara Lain (Contoh: Malaysia menggunakan State & Location)
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
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return get_faker_fallback_data()

    # 2. PERBARUI PROMPT AGAR AI MENYALIN KEY LOKASI SECARA DINAMIS
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
        "Choose Company Type": "Private",
        "Choose Language": "Indonesian",
        "Input Address": "Jl. Merdeka No 1",
        "Country": "Indonesia",
        "Choose Province": "Jawa Barat",
        "Choose City": "Bandung",
        "Choose District": "Sumur Bandung",
        "Choose Sub District": "Babakan Ciamis",
        "Choose Postal Code": "40111"
    }}
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