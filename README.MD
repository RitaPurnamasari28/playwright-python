# Unified QA Automation Framework (Web & Mobile)

Framework ini menggunakan arsitektur modular yang menggabungkan **Playwright** untuk pengujian Web dan **Maestro** 

## ⚙️ Dependencies
Pastikan sistem Anda sudah menginstal:
- pytest
- playwright
- allure-pytest
- faker
- openai

### Instalasi Python Dependencies
```bash
pip install -r requirements.txt

### playwright install
```bash
playwright install --with-deps

### how to run each suite and generate allure report
pytest tests --headed --slowmo=500 --alluredir=allure-results

### how to open the Allure report
allure serve allure-results
