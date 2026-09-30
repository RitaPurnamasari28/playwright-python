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
    with allure.step("verify login success"):
        login_page.verify_login_success()
    # ---------------------------------------------------------
    # Tier 1:
    # Meamstikan berhasil login dan halaman home terbuka
    # # ---------------------------------------------------------
