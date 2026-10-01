Framework ini menggunakan arsitektur modular yang menggabungkan **Playwright** untuk pengujian Web

1. Dependencies
Pastikan sistem Anda sudah menginstal:
- pytest
- playwright
- allure-pytest
- faker
- openai

2. Instalasi Python Dependencies
pip install -r requirements.txt
- pytest
- playwright
- allure-pytest
- faker
- google-generativeai
- python-dotenv
- pytest-playwright

3. playwright install
playwright install --with-deps

4. how to run each suite and generate allure report
pytest tests --headed --slowmo=500 --alluredir=allure-results

5. how to open the Allure report
allure serve allure-results
