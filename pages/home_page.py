from playwright.sync_api import Page, expect

class HomePage:
    def __init__(self, page: Page):
        self.page = page
        
        self.menu_companies = page.locator('a[href="/companies"]')
        
        # Contoh elemen penanda login berhasil (misal: tulisan Dashboard muncul)
        self.successopencompanies_page = page.locator("text='My Company'") 

    # --- Actions --
    def open_companies_page(self):
        self.menu_companies.click()

    # --- Assertions ---
    def verify_success_opencompanies_page(self):
        # Guardrail: Tetap strict tanpa try/except
        expect(self.successopencompanies_page).to_be_visible(timeout=10000)