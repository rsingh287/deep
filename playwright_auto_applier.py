"""
Autonomous Playwright Job Application & Form Auto-Filler
---------------------------------------------------------
Uses Playwright to navigate live job listings, click 'Apply Now',
and automatically fill in applicant details, email, phone, and AI cover letter.
"""

import os
import time

from playwright.sync_api import sync_playwright

import db_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")


def get_applicant_info():
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT full_name, email, phone, skills, experience_summary FROM user_job_profile WHERE id = 1"
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "name": row[0],
                "email": row[1],
                "phone": row[2],
                "skills": row[3],
                "summary": row[4],
            }
    except Exception:
        pass
    return {
        "name": os.getenv("APPLICANT_NAME", "IT Specialist Candidate"),
        "email": os.getenv("APPLICANT_EMAIL", "applicant@example.com"),
        "phone": os.getenv("APPLICANT_PHONE", "+1-555-0199"),
        "skills": os.getenv("APPLICANT_SKILLS", "Enterprise IT Support, Cloud Administration, Network Architecture, Jira"),
        "summary": os.getenv("APPLICANT_SUMMARY", "IT Systems Analyst and Enterprise Infrastructure Specialist"),
    }


def fill_application_form_on_page(page, cover_letter_text=""):
    """
    Finds standard input fields on job application forms and fills them automatically.
    """
    info = get_applicant_info()
    print(f"[PlaywrightApplier] Filling form for applicant: {info['name']}")

    # 1. Fill Name Fields
    name_selectors = [
        'input[name*="name" i]',
        'input[id*="name" i]',
        'input[autocomplete="name"]',
        'input[placeholder*="name" i]',
        'input[aria-label*="name" i]',
    ]
    for sel in name_selectors:
        try:
            if page.locator(sel).first.is_visible():
                page.locator(sel).first.fill(info["name"])
                print(f"  ✓ Filled Name field: {sel}")
                break
        except Exception:
            pass

    # 2. Fill Email Fields
    email_selectors = [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]',
        'input[placeholder*="email" i]',
    ]
    for sel in email_selectors:
        try:
            if page.locator(sel).first.is_visible():
                page.locator(sel).first.fill(info["email"])
                print(f"  ✓ Filled Email field: {sel}")
                break
        except Exception:
            pass

    # 3. Fill Phone Fields
    phone_selectors = [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[id*="phone" i]',
        'input[placeholder*="phone" i]',
    ]
    for sel in phone_selectors:
        try:
            if page.locator(sel).first.is_visible():
                page.locator(sel).first.fill(info["phone"])
                print(f"  ✓ Filled Phone field: {sel}")
                break
        except Exception:
            pass

    # 4. Fill Cover Letter / Summary Textarea
    cover_selectors = [
        'textarea[name*="cover" i]',
        'textarea[id*="cover" i]',
        'textarea[name*="letter" i]',
        'textarea[placeholder*="cover" i]',
        'textarea[aria-label*="cover" i]',
    ]
    for sel in cover_selectors:
        try:
            if page.locator(sel).first.is_visible():
                page.locator(sel).first.fill(cover_letter_text)
                print(f"  ✓ Auto-Pasted Cover Letter into textarea: {sel}")
                break
        except Exception:
            pass

    # 5. Fill Indeed 'Reason for applying' / 'Why are you applying' Textarea
    reason_selectors = [
        'textarea[name*="reason" i]',
        'textarea[id*="reason" i]',
        'textarea[aria-label*="reason" i]',
        'textarea[placeholder*="reason" i]',
        'textarea[name*="why" i]',
        'textarea[id*="why" i]',
        "textarea",
    ]
    default_reason = (
        f"I am applying because my hands-on technical experience in telecommunications field service (Bell BTS), "
        f"Computer Engineering Technician diploma from Niagara College, Google IT Support Certificate, "
        f"and Ontario Class G Driver's License align directly with your field service and IT operations requirements in Greater Sudbury."
    )
    for sel in reason_selectors:
        try:
            if page.locator(sel).first.is_visible():
                page.locator(sel).first.fill(default_reason)
                print(f"  ✓ Auto-filled 'Reason for applying' textarea: {sel}")
                break
        except Exception:
            pass


def auto_apply_with_playwright(target_url, cover_letter=""):
    """
    Launches browser via Playwright, opens target job page, clicks Apply, and auto-fills fields.
    """
    print(
        f"[PlaywrightApplier] Launching automated browser for target URL: {target_url}"
    )
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--start-maximized"])
            context = browser.new_context(no_viewport=True)
            page = context.new_page()

            page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)

            # Try to locate and click 'Apply Now' / 'Apply with Indeed' / 'Easily Apply' button
            apply_selectors = [
                'button:has-text("Apply Now")',
                'button:has-text("Apply with Indeed")',
                'a:has-text("Apply Now")',
                'button:has-text("Easily apply")',
                'button[id*="apply"]',
                'a[id*="apply"]',
            ]

            for sel in apply_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible():
                        btn.click()
                        print(f"  ✓ Auto-clicked Apply button: {sel}")
                        time.sleep(3)
                        break
                except Exception:
                    pass

            # Auto-fill form fields
            fill_application_form_on_page(page, cover_letter)

            print("[PlaywrightApplier] Form fields auto-filled successfully!")
            time.sleep(5)
            browser.close()
            return True
    except Exception as e:
        print(f"[PlaywrightApplier] Error during auto-apply: {e}")
        return False


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    test_url = "https://ca.indeed.com/jobs?q=IT+Support&l=Greater+Sudbury%2C+ON"
    auto_apply_with_playwright(
        test_url, "Dear Hiring Manager, I am applying for the IT Support position..."
    )
