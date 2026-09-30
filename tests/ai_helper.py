import os
import json
import random
from faker import Faker
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi agar Python membaca API Key dari file .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
fake = Faker()

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
        "Choose Province": "Papua", 
        "Choose City": "Jayapura", 
        "Choose District": "Abepura", 
        "Choose Sub District": "Koya Koso", 
        #"Choose Postal Code": "99112"
    },
    {
        "Country": "Malaysia", 
        "Choose State": "Selangor", 
        "Choose City": "Petaling Jaya", 
        "Choose Location": "Damansara", 
        #"Choose Postal Code": "47400"
    },
    {
        "Country": "Philippines",
        "Choose Region": "Metro Manila",
        "Choose Province": "Metro Manila",
        "Choose City": "Makati",
        "Choose Barangay": "Bel-Air",
        #"Choose Postal Code": "1209"
    },
    {
        "Country": "Cambodia",
        "Choose Province": "Phnom Penh",
        "Choose District": "Chamkar Mon",
        "Choose Commune": "Tonle Basak",
        #"Choose Postal Code": "120101"
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
        "Input Company Name": fake.company()[:12],
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
    try:
        # Menggunakan Gemini 1.5 Flash (sangat cepat dan gratis)
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        # Perhatikan instruksi max 25 characters agar tidak gagal di UI
        prompt = """
        Generate random company data for registration form in JSON format.
        Rules:
        1. "Input Company Name": Random company name, maximum 25 characters.
        2. "Input Email": Random professional email.
        Return ONLY a valid JSON object.
        """
        
        # Temperature 0.7 memastikan datanya selalu random/acak setiap kali dijalankan
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7 
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Gemini API gagal, menggunakan Faker... Error: {e}")
        # Jika kuota habis atau internet putus, otomatis pakai data Faker
        return get_faker_fallback_data()
