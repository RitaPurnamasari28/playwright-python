# AI Usage Documentation - eDOT E2E Automation Framework
1. Which model you used and why
For this project, I used Gemini. I am still evaluating which AI best suits this scenario, and I plan to test other models in the future. The goal is to find the most cost-efficient and capable AI for these specific testing needs.

2. AI for Test Data Generation (`ai_helper.py`)
- **Primary Mechanism:** The OpenAI API generates realistic data strings based on specific context prompts.
- **Deterministic Fallback:** If the `GEMINI_API_KEY` is missing (e.g., in offline mode, local runs, or specific CI environments), the system automatically falls back to the `Faker` library. This guarantees that test execution is 100% deterministic and never blocked by AI service unavailability or network issues.

3. AI-Assisted Failure Triage (`triage.py`)
Post-execution test failures are analyzed automatically to accelerate the debugging process and provide actionable insights for the engineering team.
- **Analysis Scope:** AI reads the test execution logs and stack traces to propose a root cause (e.g., Locator Timeout, Element Not Visible, Assertion Failure).
- **Reporting:** The analysis generates a structured `triage_report.md` artifact
- **Deterministic Fallback:** A built-in local deterministic decision tree handles the triage process gracefully if the API is unreachable, ensuring continuous reporting without failure.

4. Strict QA Guardrails & Constraints
The integration of AI in this framework is strictly bounded by the following constraints to maintain the absolute integrity of the QA process:
- **No Automated Assertion Modification:** AI is strictly prohibited from altering, relaxing, or skipping test assertions. Tests will only pass or fail based on hardcoded, deterministic logical validations.
- **No Auto-Filing of Bugs:** AI provides post-run analysis and verdict proposals only. It does not automatically create tickets in bug tracking systems (e.g., Jira/Trello). A human QA Engineer must always review the AI triage and validate the final defect report.
- **Execution Determinism:** The framework architecture ensures the test flow remains deterministic. AI influences only the *data inputs* and *post-execution analysis*, never the sequence, actions, or state machine of the test execution itself.