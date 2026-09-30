import os
import json
import random
from faker import Faker
from openai import OpenAI

def get_faker_fallback_data():
    """Deterministic fallback using Faker."""
    print("\n[INFO] API Key tidak ditemukan atau API gagal. Menggunakan Deterministic Fallback (Faker)...")
    
    # Supaya benar-benar 'deterministic' (hasilnya konsisten dan bisa diprediksi untuk testing)
    # kita bisa set seed opsional jika diperlukan, tapi random biasa sudah cukup baik.
    fake = Faker('en_US')
    Faker.seed(42) # Opsional: Membuat data Faker selalu sama setiap di-run (sangat disukai di CI)
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
        "Choose Company Type": "Private",     
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
    # 1. Cek keberadaan API Key secara eksplisit (Menjawab requirement test)
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        return get_faker_fallback_data()

    # 2. Jika API Key ada, coba gunakan AI
    prompt = """
    Kamu adalah asisten QA Automation. Hasilkan JSON data perusahaan dummy.
    Negara wajib dari: Cambodia, Indonesia, Malaysia, Philippines.
    Format Key wajib:
    "Input Company Name", "Input Email", "phone_country_code", "Input Phone",
    "Choose Industry Type", "Choose Company Type", "Choose Language", "Input Address",
    "Country", "Choose State", "Choose City", "Choose Location", "Choose Postal Code"
    """

    try:
        # Client bisa diarahkan ke OpenAI asli atau Groq tergantung key yang dipasang
        client = OpenAI(api_key=api_key, timeout=5.0)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Atau model lain yang didukung
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        print("\n[INFO] Berhasil menggunakan AI untuk generate data!")
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        # 3. Fallback kedua jika API Key ada tapi saldonya habis (error 429) atau timeout
        print(f"\n[WARNING] Eksekusi API gagal ({e}). Beralih ke Fallback...")
        return get_faker_fallback_data()