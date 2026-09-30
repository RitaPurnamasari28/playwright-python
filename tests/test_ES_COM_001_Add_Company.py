from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.companies_page import CompaniesPage
from playwright.sync_api import expect
from ai_helper import generate_full_company_data
from pages.companies_page import CompaniesPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import allure

def test_add_company(page):
    # 1. Inisialisasi POM Login
    login_page = LoginPage(page)
    login_email = "it.qa@edot.id"
    login_password = "it.QA2025"
        
    with allure.step("Open esuite"):
        login_page.navigate()
    with allure.step("input email and password then click login button"):
        login_page.do_login(login_email, login_password)
    with allure.step("ver"):
        login_page.verify_login_success()

# 4. open companies menu
    home_page = HomePage(page)
    with allure.step("open companies menu"):
        home_page.open_companies_page()
    with allure.step("verify success open companies page"):
        home_page.verify_success_opencompanies_page()
    ai_data = generate_full_company_data()
    company_name = ai_data["Input Company Name"]

    # 3. Eksekusi pengisian form otonom
    companies_page = CompaniesPage(page)
    with allure.step("click add company button"):
        companies_page.add_company_btn()
    with allure.step("fill form company data"):
        companies_page.fill_form_autonomously(ai_data)

    # 4. Lanjut ke step berikutnya
    with allure.step("Click next button"):
        companies_page.click_next()
    with allure.step("click next button on page two"):
        companies_page.page_two()
    with allure.step("input branch data same with company data, select checkbox then click register"):
        companies_page.page_three()
    # 5. Assertion: Pastikan data sukses disimpan (Misal: mengecek nama company muncul di halaman berikutnya)
        mycompany_header = page.get_by_text("My Company", exact=True)
        expect(mycompany_header).to_be_visible()
    with allure.step("Open company detail page"):
        companies_page.buka_detail_perusahaan(company_name)
        print("\n[INFO] Memvalidasi data tersimpan di halaman detail...")
        expect(page.locator("h1")).to_contain_text(company_name)
    with allure.step("Validate saved company data"):
    # Validasi dinamis untuk semua value yang di-generate
        for key, value in ai_data.items():
        # Lewati validasi otomatis untuk field yang format tampilannya berubah di UI
            if key in ["phoneNumber", "phone_country_code"]:
                continue
            
            print(f"Memastikan teks muncul di layar: {value}")
            elemen_teks = page.get_by_text(str(value), exact=False).first
            expect(elemen_teks).to_be_visible()
    with allure.step("Delete company after validation"):
        companies_page.delete_company()
