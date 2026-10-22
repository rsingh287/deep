"""
Comprehensive Verification Suite for Upgraded dom_system_engine.py & Crawl4ai
"""

import os
import sys

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import dom_system_engine


def run_tests():
    print("===============================================================")
    print("🧪 STARTING VERIFICATION: AGENTIC BROWSER LOOP & CRAWL4AI")
    print("===============================================================\n")

    # TEST 1: Crawl4ai Clean Markdown Extraction
    print("--- [TEST 1] Crawl4ai Clean Markdown Extraction ---")
    crawl_res = dom_system_engine.extract_clean_markdown("https://httpbin.org/html")
    assert crawl_res.get("status") == "success", f"Crawl failed: {crawl_res}"
    print(f"✓ Crawl4ai Engine: {crawl_res.get('engine')}")
    print(f"✓ Extracted Markdown Length: {crawl_res.get('char_count')} characters")
    print(f"✓ Markdown Sample: {crawl_res.get('markdown', '')[:120].strip()}...\n")

    # TEST 2: Existing inspect_dom_tree Backward Compatibility
    print("--- [TEST 2] Backward Compatibility (inspect_dom_tree) ---")
    html_path = os.path.abspath("test_autonomous_form.html").replace("\\", "/")
    file_url = f"file:///{html_path}"
    inspect_res = dom_system_engine.inspect_dom_tree(file_url)
    assert "input_count" in inspect_res, f"inspect_dom_tree failed: {inspect_res}"
    print(f"✓ Target: {file_url}")
    print(f"✓ Inputs Found: {inspect_res.get('input_count')}")
    print(f"✓ Buttons Found: {inspect_res.get('button_count')}")
    print(f"✓ Textareas Found: {len(inspect_res.get('textareas', []))}\n")

    # TEST 3: Autonomous Agentic Browser Form Filling Loop
    print("--- [TEST 3] Autonomous Agentic Form Filling Loop ---")
    test_data = {
        "full_name": os.getenv("APPLICANT_NAME", "Alex Taylor"),
        "email": os.getenv("APPLICANT_EMAIL", "alex.taylor@example.com"),
        "phone": os.getenv("APPLICANT_PHONE", "+1-555-0199"),
        "topic": "AI Consulting",
        "message": "Automated test message generated via Antigravity Agentic Browser Loop.",
    }

    loop_res = dom_system_engine.autonomous_agentic_browser_loop(
        url=file_url,
        task_instruction="Fill out all contact inquiry fields with the applicant's details, select AI Consulting, and click Send Inquiry.",
        form_data=test_data,
        max_steps=8,
        headless=True,
    )

    print("\n--- Agentic Execution Results ---")
    print(f"Status: {loop_res.get('status')}")
    print(f"Total Steps Taken: {loop_res.get('total_steps')}")
    print(f"Page Title: {loop_res.get('page_title')}")
    print("Execution History:")
    for step in loop_res.get("steps_log", []):
        print(
            f"  - Step {step.get('step')}: [{step.get('action').upper()}] Value: '{step.get('value')}' | Status: {step.get('status', 'OK')}"
        )

    assert loop_res.get("status") == "success", f"Agentic loop failed: {loop_res}"
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
