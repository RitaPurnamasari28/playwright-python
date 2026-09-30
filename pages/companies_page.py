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

    def fill_form_autonomously(self, ai_generated_data):
        """Membaca JSON dan mengeksekusi input otomatis"""
        # wait for add company form loaded
        self.page.wait_for_timeout(1000) 
        
        for key, value in ai_generated_data.items():
            print(f"Mengisi {key} dengan {value}...")
            
            # 1. Dropdown Bendera Telepon (Berdasarkan Index)
            if key == "phone_country_code":
                self.page.locator('button[role="combobox"]').filter(has=self.page.locator("img")).click()
                self.page.wait_for_timeout(500) # Tunggu animasi dropdown
                
                # Pemetaan urutan bendera berdasarkan UI (0=Indonesia, 1=Philippines, 2=Malaysia, 3=Cambodia)
                country_idx = {
                    "Indonesia": 0,
                    "Philippines": 1,
                    "Malaysia": 2,
                    "Cambodia": 3
                }
                idx = country_idx.get(value, 0)
                
                # Klik opsi berdasarkan index urutannya
                self.page.get_by_role("option").nth(idx).click()
                continue
                
            # 2. Dropdown Country Utama
            if key == "Country":
                # Langsung target combobox dengan teks spesifik dan amankan dengan .first
                dropdown = self.page.locator('button[role="combobox"]').filter(has_text="Choose Country").first
                
                dropdown.wait_for(state="visible")
                dropdown.click()
                self.page.wait_for_timeout(500)
                
                # Gunakan exact=False dan .first sama seperti aturan dropdown lainnya
                self.page.get_by_role("option", name=value, exact=False).first.click()
                self.page.wait_for_timeout(1000) 
                continue

            # 3. Text Input (Company Name, Email, Phone, Address)
            if "Input" in key:
                input_field = self.page.get_by_placeholder(key)
                input_field.wait_for(state="visible")
                
                # Klik dulu formnya untuk memancing fokus, lalu beri jeda sangat singkat
                input_field.click()
                self.page.wait_for_timeout(200)
                
                # Gunakan press_sequentially agar mengetik seperti manusia sungguhan (mencegah field terhapus sistem)
                input_field.clear()
                input_field.press_sequentially(value, delay=50)
                continue
                
            # 4. Dropdown lainnya (Industry, State, City, dll)
            if "Choose" in key:
                # Tambahkan .first dan .wait_for() untuk memastikan Playwright mengklik elemen yang benar-benar aktif di layar
                dropdown = self.page.locator('button[role="combobox"]').filter(has_text=key).first
                dropdown.wait_for(state="visible")
                dropdown.click()
                
                self.page.wait_for_timeout(1000) # Tambah jeda sedikit lebih lama untuk memastikan animasi dropdown selesai
                
                # HAPUS exact=True (atau set exact=False) dan tambahkan .first
                # Ini akan mengatasi masalah spasi tak terlihat atau duplikasi elemen di DOM
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

    def open_company_detail(self):
        print("Menunggu halaman stabil...")
        self.page.wait_for_timeout(3000)
    
    # 1. Paksa scroll ke paling bawah agar aplikasi memuat UI-nya
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(2000) # Kasih jeda agar render selesai
    
    # 2. Fokus SATU kartu saja, yaitu kartu urutan paling akhir (.last)
        kartu_terakhir = self.page.locator("div.bg-card").last
    
    # 3. KRUSIAL: Pastikan kartu ini benar-benar ditarik masuk ke tengah layar
        kartu_terakhir.scroll_into_view_if_needed()
    
    # 4. Ambil tombol Manage di dalam kartu terakhir tersebut
        tombol_manage = kartu_terakhir.get_by_role("button", name="Manage")
    
    # 5. Hajar kliknya! Gunakan force=True untuk menembus halangan apapun
        print("Mengeklik tombol Manage pada data paling bawah...")
        tombol_manage.click(force=True)
    
    # 6. Tangani halaman loading "Please wait..." setelah diklik
        loading_text = self.page.get_by_text("Please wait...", exact=False).first
        if loading_text.is_visible():
            loading_text.wait_for(state="hidden", timeout=15000)
        

    def delete_company(self):
        self.delete_company_btn.click()

    

    

    