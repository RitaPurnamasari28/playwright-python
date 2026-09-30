import os
import glob
import json
import google.generativeai as genai
from dotenv import load_dotenv

def fallback_triage(test_name, error_message):
    """Logika triase lokal (tanpa API) sesuai dengan urutan dari soal."""
    error_lower = error_message.lower()
    
    # 1. Exception (element not found, timeout) or failed assertion?
    if "timeout" in error_lower or "not found" in error_lower or "waiting for" in error_lower or "keyerror" in error_lower or "exception" in error_lower:
        verdict = "Script/Environment Defect"
        evidence = "Fallback Logic: Exception detected (timeout/element not found). The locator likely failed to resolve, indicating a script or environment issue."
    
    # 2. Failed Assertion?
    elif "assert" in error_lower or "expected" in error_lower:
        verdict = "Product Bug (or Flaky)"
        evidence = "Fallback Logic: Failed assertion detected. The locator resolved and steps succeeded, but the actual value differed from expected. Requires manual check for consistency."
    
    else:
        verdict = "Script/Environment Defect"
        evidence = "Fallback Logic: Unknown exception occurred causing the script to halt."

    return f"### Test: {test_name}\n**Verdict:** [{verdict}]\n**Evidence:** {evidence}\n**Raw Error:** `{error_message.splitlines()[0] if error_message else 'None'}`"

def run_triage():
    api_key = os.getenv("GEMINI_API_KEY")
    allure_results_dir = "allure-results"
    
    # Inisialisasi client HANYA jika api_key ada
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel("gemini-pro") if api_key else None
    
    result_files = glob.glob(os.path.join(allure_results_dir, "*-result.json"))
    
    report_content = "# AI Test Failure Triage Report\n\n"
    report_content += "> *Note: This is a proposal for human review. No bugs have been auto-filed.*\n\n"
    
    has_failures = False

    for file_path in result_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        status = data.get("status")
        if status in ["failed", "broken"]:
            has_failures = True
            test_name = data.get("name", "Unknown Test")
            error_message = data.get("statusDetails", {}).get("message", "No message")
            trace = data.get("statusDetails", {}).get("trace", "No trace")
            
            # --- JIKA PUNYA API KEY ---
            if client:
                prompt = f"""
                You are a QA Triage Assistant. Analyze the following test failure and assign a verdict: 
                [script/environment defect], [product bug], or [flaky].
                
                Evaluate strictly in this order and stop at the first match:
                1. Exception (element not found, timeout) or failed assertion? (Exception -> mostly script/env)
                2. Did the locator resolve to the intended, unique element?
                3. Did every step before the assertion succeed?
                4. Was the expected value correct according to the test case?
                5. Does it reproduce consistently? (Intermittent -> flaky).
                
                Test Name: {test_name}
                Error Message: {error_message}
                Stack Trace: {trace[:1000]}
                
                Output format (Markdown):
                ### Test: {test_name}
                **Verdict:** [Your Verdict]
                **Evidence:** [Brief explanation of your finding based on the trace]
                """
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                        max_tokens=250
                    )
                    report_content += response.choices[0].message.content + "\n\n---\n\n"
                except Exception as e:
                    print(f"[WARNING] OpenAI API gagal memproses ({str(e)}). Beralih ke Fallback Triase Lokal.")
                    report_content += fallback_triage(test_name, error_message) + "\n\n---\n\n"
            
            # --- JIKA TIDAK PUNYA API KEY (KONDISIMU SAAT INI) ---
            else:
                print("[INFO] Tidak ada API Key. Menggunakan Fallback Triase Lokal.")
                report_content += fallback_triage(test_name, error_message) + "\n\n---\n\n"
            
    if not has_failures:
        report_content += "🎉 **No failures detected in this run. Great job!**\n"
        
    with open("triage_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("\n[SUCCESS] Triage report generated: triage_report.md")

if __name__ == "__main__":
    run_triage()