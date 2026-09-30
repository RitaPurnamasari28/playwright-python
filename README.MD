# Unified QA Automation Framework (Web & Mobile)

Framework ini menggunakan arsitektur modular yang menggabungkan **Playwright** untuk pengujian Web dan **Maestro** untuk pengujian Mobile. Seluruh eksekusi dibungkus menggunakan **Pytest** dan dilengkapi dengan pelaporan **Allure**.

## ⚙️ Prerequisites & Dependencies
Pastikan sistem Anda sudah menginstal:
- Python 3.10+
- Java (JDK 11+) untuk Allure
- Android Studio / SDK Command-Line Tools (untuk ADB & Emulator)

### Instalasi Python Dependencies
```bash
pip install -r requirements.txt

### playwright install
```bash
playwright install --with-deps

### how to run each suite
pytest tests/test_ES_LOG_001_Login.py --headed --slowmo=500 --alluredir=allure-results

### how to generate and open the Allure report
allure generate allure-results --clean -o allure-report
allure open allure-report