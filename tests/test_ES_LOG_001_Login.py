from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.companies_page import CompaniesPage
from playwright.sync_api import expect
from ai_helper import generate_full_company_data
from pages.companies_page import CompaniesPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import allure

def test_login_valid_credentials(page):
    # 1. Inisialisasi POM Login
    login_page = LoginPage(page)
    
    # 2. Set email dan password Anda secara langsung (hardcode)
    
    
    login_email = "it.qa@edot.id"
    login_password = "it.QA2025U"
    
    # 3. Eksekusi Test Steps
    login_page.navigate()
    login_page.do_login(login_email, login_password)
    login_page.verif_login_success()
    
    
