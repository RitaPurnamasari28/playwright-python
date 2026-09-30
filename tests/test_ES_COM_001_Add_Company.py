from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.companies_page import CompaniesPage
from playwright.sync_api import expect
from ai_helper import generate_full_company_data
from pages.companies_page import CompaniesPage
from pages.login_page import LoginPage
from playwright.sync_api import expect

def test_add_company(page):
    # 1. Inisialisasi POM Login
    login_page = LoginPage(page)
        
        # 2. Set email dan password Anda secara langsung (hardcode)
    login_email = "it.qa@edot.id"
    login_password = "it.QA2025"
        
        # 3. Eksekusi Test Steps
    login_page.navigate()
    login_page.do_login(login_email, login_password)

    login_page.verif_login_success()

# 4. open companies menu
    home_page = HomePage(page)
    home_page.open_companies_page()
    home_page.verify_login_success()
    ai_data = generate_full_company_data()
    company_name = ai_data["Input Company Name"]

    # 3. Eksekusi pengisian form otonom
    companies_page = CompaniesPage(page)
    companies_page.add_company_btn()
    companies_page.fill_form_autonomously(ai_data)
    
    # 4. Lanjut ke step berikutnya
    companies_page.click_next()
    companies_page.page_two()
    companies_page.page_three()

    
    # 5. Assertion: Pastikan data sukses disimpan (Misal: mengecek nama company muncul di halaman berikutnya)
    mycompany_header = page.get_by_text("My Company", exact=True)
    expect(mycompany_header).to_be_visible()

    companies_page.buka_detail_perusahaan(company_name)

    print("\n[INFO] Memvalidasi data tersimpan di halaman detail...")
    expect(page.locator("h1")).to_contain_text(company_name)

    # Validasi dinamis untuk semua value yang di-generate
    for key, value in ai_data.items():
        # Lewati validasi otomatis untuk field yang format tampilannya berubah di UI
        if key in ["phoneNumber", "phone_country_code"]:
            continue
            
        print(f"Memastikan teks muncul di layar: {value}")
        elemen_teks = page.get_by_text(str(value), exact=False).first
        expect(elemen_teks).to_be_visible()

    companies_page.delete_company()
