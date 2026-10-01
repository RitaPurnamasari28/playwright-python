from pages.home_page import HomePage
from ai_helper import generate_full_company_data
from pages.companies_page import CompaniesPage
from pages.login_page import LoginPage
from playwright.sync_api import expect
import allure


def test_add_company(page):
    # Login data
    login_page = LoginPage(page)
    login_email = "it.qa@edot.id"
    login_password = "it.QA2025"
    # login flow
    with allure.step("Open esuite"):
        login_page.navigate()
    with allure.step("input email and password then click login button"):
        login_page.do_login(login_email, login_password)
    with allure.step("verify login success"):
        login_page.verify_login_success()

    # Open companies menu
    home_page = HomePage(page)
    with allure.step("open companies menu"):
        home_page.open_companies_page()
    with allure.step("verify success open companies page"):
        home_page.verify_success_opencompanies_page()

    # Fill form company data PAGE 1
    companies_page = CompaniesPage(page)
    ai_data = generate_full_company_data()
    companies_page.add_company_btn()
    with allure.step("fill form company data"):
        # get data dummy from ai_helper.py
        ai_data = generate_full_company_data()
        company_name = ai_data["Input Company Name"]
        # fill the data to the form
        companies_page.fill_form_autonomously(ai_data)
    with allure.step("Click next button"):
        companies_page.click_next()
    # Fill form company data PAGE 2
    with allure.step("click next button on page two"):
        companies_page.page_two()
    # Fill form company data PAGE 3
    with allure.step(
        "input branch data same with company data, select checkbox then click register"
    ):
        companies_page.page_three()
    # open company detail page and validate saved data
    with allure.step("Open company detail page"):
        companies_page.open_company_detail(company_name)
        # check if company name is displayed on the detail page
        expect(page.locator("h1")).to_contain_text(company_name)
    with allure.step("Validate saved company data"):
        # bot read data cummy created
        for key, value in ai_data.items():
            print(f"Memastikan teks muncul di layar: {value}")
            # check the data one by one if it is displayed on the screen
            elemen_teks = page.get_by_text(str(value), exact=False).first
            # ensure all the data saved is visible on the screen
            expect(elemen_teks).to_be_visible()

    # ---------------------------------------------------------
    # Tier 2:
    # Memastikan company berhasil tersimpan dan data yang di simpan benar sesuai dengan data yang di-generate AI atau faker
    # # ---------------------------------------------------------
    with allure.step("Delete company after validation"):
        companies_page.delete_company()
