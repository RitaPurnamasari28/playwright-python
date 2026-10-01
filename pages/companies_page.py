from pytest_playwright.pytest_playwright import page


class CompaniesPage:
    def __init__(self, page):
        self.page = page
        # Locators
        self.addcompany_btn = page.locator("button:text('Add Company')")
        self.btn_next = page.get_by_role("button", name="Next") 
        self.usecompanydata_btn = page.locator("button:text('Fill in with the same data from the Company records')")
        self.checkbox = page.locator("#select-all")
        self.register_btn = page.locator("button:text('Register')")
        self.delete_company_btn = page.locator("button:text('Delete')")



    def add_company_btn(self):
            self.addcompany_btn.click()

# Locator and action for add company page. page 1
    def fill_form_autonomously(self, ai_generated_data):
        self.page.wait_for_timeout(1000) 
        
        for key, value in ai_generated_data.items():
            print(f"Mengisi {key} dengan {value}...")
            
            # 1. flag dropdown for phone area code
            if key == "phone_country_code":
                self.page.locator('button[role="combobox"]').filter(has=self.page.locator("img")).click()
                self.page.wait_for_timeout(500)
                
                # set the Flag index for each country to click the correct option
                country_idx = {
                    "Indonesia": 0,
                    "Philippines": 1,
                    "Malaysia": 2,
                    "Cambodia": 3
                }
                idx = country_idx.get(value, 0) 
                
                # Click option base on option
                self.page.get_by_role("option").nth(idx).click()
                continue
                
            # 2. Country dropdown
            if key == "Country":
                # Target  first combobox
                dropdown = self.page.locator('button[role="combobox"]').filter(has_text="Choose Country").first
                
                dropdown.wait_for(state="visible")
                dropdown.click()
                self.page.wait_for_timeout(500)
                
                # choosing from value, choose same value with phone number country
                self.page.get_by_role("option", name=value, exact=False).first.click()
                self.page.wait_for_timeout(1000) 
                continue

            # 3. Text Input (Company Name, Email, Phone, Address)
            if "Input" in key:
                input_field = self.page.get_by_placeholder(key)
                input_field.wait_for(state="visible")
                
                input_field.click()
                self.page.wait_for_timeout(200)
                
                # type word by word to prevent detected as bot. just for prevention
                input_field.clear()
                input_field.press_sequentially(value, delay=50)
                #stop looping
                continue
                
            # 4. Other dropdown (Industry, State, City, dll)
            if "Choose" in key:
                dropdown = self.page.locator('button[role="combobox"]').filter(has_text=key).first
                dropdown.wait_for(state="visible")
                dropdown.click()
                
                self.page.wait_for_timeout(1000)
                
                opsi_dropdown = self.page.get_by_role("option", name=value, exact=False).first
                opsi_dropdown.click()
                
                if key in ["Choose State", "Choose City", "Choose Location"]:
                    self.page.wait_for_timeout(1000)

    def click_next(self):
        self.btn_next.click()

    def page_two(self):
        self.btn_next.click()

    def page_three(self):
        self.usecompanydata_btn.click()
        self.checkbox.click()
        self.register_btn.click()
        self.page.wait_for_timeout(30000)

    def open_company_detail(self): # i still getting the last card here. if test is run the flow will stuck here
        print("Wait for page loaded")
        self.page.wait_for_timeout(3000)
    
    # 1. Scroll to end of the page
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(2000) # Kasih jeda agar render selesai
    
    # 2. focus to the last card
        last_card = self.page.locator("div.bg-card").last
    
    # 3. Make the last card in view (scroll into view if needed)
        last_card.scroll_into_view_if_needed()
    
    # 4. Find the "Manage" button within the last card
        tombol_manage = last_card.get_by_role("button", name="Manage")
    
    # 5. Click the "Manage" button
        tombol_manage.click(force=True)
    
    # 6. wait for the loading text to disappear
        loading_text = self.page.get_by_text("Please wait...", exact=False).first
        if loading_text.is_visible():
            loading_text.wait_for(state="hidden", timeout=15000)
        

    def delete_company(self):
        self.delete_company_btn.click()

    

    

    