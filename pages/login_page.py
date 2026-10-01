#locator and action
from playwright.sync_api import Page, expect


class LoginPage:

    def __init__(self, page: Page):
        self.page = page

        # --- Locators ---
        self.loginuseemailorpassword_btn = page.locator(
            "button:text('Use Email or Username')"
        )

        self.email_input = page.locator("input[name='username']")
        self.login1_btn = page.locator("button:text('Log In')")
        self.password_input = page.locator("input[name='password']")
        self.login2_btn = page.locator("button:text('Log In')")
        self.welcome_element = page.locator("text='Welcome Back,'")

    # --- Actions ---
    def navigate(self):
        self.page.goto("https://esuite.edot.id/")

    def do_login(self, email: str, password: str):
        self.loginuseemailorpassword_btn.click()
        self.email_input.wait_for(state="visible")
        self.email_input.fill(email)
        self.login1_btn.click()
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)
        self.login2_btn.click()

    # --- Assertions ---
    def verify_login_success(self):
        expect(self.welcome_element).to_be_visible(timeout=40000)
