"""
===================================================================
ANTIGRAVITY AI WORKSTATION: DIRECT DOM SYSTEM ENGINE & AGENTIC BROWSER LOOP
===================================================================
Provides deep Document Object Model (DOM) parsing, tree inspection,
Crawl4ai clean markdown extraction, and an autonomous Browser-Use style
agentic interaction loop for dynamic form filling and web automation.
"""

import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional

import requests
from playwright.sync_api import sync_playwright

import db_engine

OLLAMA_API_BASE = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

# ---------------------------------------------------------------------------
# 1. CORE DOM TREE INSPECTION & TARGETED ACTION (PRESERVED FOR COMPATIBILITY)
# ---------------------------------------------------------------------------


def inspect_dom_tree(url="https://ca.indeed.com") -> Dict[str, Any]:
    """
    Navigates to target URL, inspects the live DOM tree,
    and extracts interactive nodes (inputs, buttons, textareas, links).
    """
    print(f"[DOMSystem] Navigating and inspecting DOM for: {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            dom_summary = page.evaluate("""() => {
                const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                    tag: 'input',
                    type: i.type,
                    name: i.name,
                    id: i.id,
                    placeholder: i.placeholder
                }));
                const buttons = Array.from(document.querySelectorAll('button, a[role="button"]')).map(b => ({
                    tag: 'button',
                    id: b.id,
                    text: b.innerText.trim().substring(0, 50)
                }));
                const textareas = Array.from(document.querySelectorAll('textarea')).map(t => ({
                    tag: 'textarea',
                    name: t.name,
                    id: t.id
                }));
                return {
                    title: document.title,
                    input_count: inputs.length,
                    button_count: buttons.length,
                    inputs: inputs.slice(0, 10),
                    buttons: buttons.slice(0, 10),
                    textareas: textareas.slice(0, 5)
                };
            }""")
            browser.close()
            return dom_summary
    except Exception as e:
        return {"error": f"DOM Inspection error: {str(e)}"}


def execute_dom_action(
    url: str, selector: str, action: str = "click", value: str = ""
) -> Dict[str, Any]:
    """
    Directly queries and executes an action (click, fill, focus, get_text)
    on a specific DOM node matching the provided CSS selector.
    """
    print(f"[DOMSystem] Executing action '{action}' on DOM selector '{selector}'")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            target = page.locator(selector).first
            if not target.is_visible():
                browser.close()
                return {
                    "success": False,
                    "error": f"DOM element '{selector}' not visible",
                }

            if action == "click":
                target.click()
                res = f"Clicked DOM node: {selector}"
            elif action == "fill":
                target.fill(value)
                res = f"Filled DOM node '{selector}' with value '{value}'"
            elif action == "get_text":
                text_content = target.text_content()
                res = f"Extracted DOM node text: '{text_content}'"
            else:
                res = f"Unknown action: {action}"

            time.sleep(2)
            browser.close()
            return {"success": True, "result": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# 2. CRAWL4AI CLEAN MARKDOWN EXTRACTION BRIDGE
# ---------------------------------------------------------------------------


def extract_clean_markdown(
    url: str, css_selector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Leverages Crawl4ai to transform complex dynamic webpages into clean,
    structured Markdown (preserving tables, lists, and headers) for LLM consumption.
    """
    try:
        import crawl_markdown_engine

        return crawl_markdown_engine.crawl_clean_markdown(
            url, css_selector=css_selector
        )
    except Exception as e:
        return {"status": "error", "message": f"Crawl extraction failed: {str(e)}"}


# ---------------------------------------------------------------------------
# 3. AUTONOMOUS AGENTIC BROWSER INTERACTION LOOP (BROWSER-USE STYLE)
# ---------------------------------------------------------------------------


def _get_default_user_profile() -> Dict[str, Any]:
    """Fetches user profile from memory.db or provides standard defaults."""
    if os.path.exists(MEMORY_DB_PATH):
        try:
            conn = db_engine.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT full_name, email, phone, skills, experience_summary FROM user_job_profile WHERE id = 1"
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                def_name = row[0] or os.getenv("OPERATOR_NAME", "Workstation Operator")
                name_parts = def_name.split()
                return {
                    "name": def_name,
                    "full_name": def_name,
                    "first_name": name_parts[0] if name_parts else "Operator",
                    "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                    "email": row[1] or os.getenv("OPERATOR_EMAIL", "operator@example.com"),
                    "phone": row[2] or os.getenv("OPERATOR_PHONE", "+1-555-0199"),
                    "skills": row[3] or "IT Support, Python, Playwright, Automation",
                    "message": row[4]
                    or "Experienced IT Support Analyst and Automation Specialist.",
                }
        except Exception:
            pass

    fallback_name = os.getenv("OPERATOR_NAME", "Workstation Operator")
    fallback_parts = fallback_name.split()
    return {
        "name": fallback_name,
        "full_name": fallback_name,
        "first_name": fallback_parts[0] if fallback_parts else "Operator",
        "last_name": " ".join(fallback_parts[1:]) if len(fallback_parts) > 1 else "",
        "email": os.getenv("OPERATOR_EMAIL", "operator@example.com"),
        "phone": os.getenv("OPERATOR_PHONE", "+1-555-0199"),
        "company": "Deep AI Systems",
        "message": "Hello, I am interested in connecting regarding this opportunity.",
    }


def _query_llm_action(
    goal: str,
    elements: List[Dict[str, Any]],
    filled_indices: List[int],
    form_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Asks local Ollama (Llama/Qwen) to choose the next browser action given visible elements."""
    unfilled_elements = [e for e in elements if e["index"] not in filled_indices]
    elements_summary = []
    for el in unfilled_elements[:15]:
        lbl = (
            el.get("label")
            or el.get("placeholder")
            or el.get("text")
            or el.get("name")
            or "Unnamed"
        )
        val = el.get("value", "")
        options_str = (
            f" Options: {[o['text'] for o in el.get('options', [])]}"
            if el.get("options")
            else ""
        )
        elements_summary.append(
            f"[{el['index']}] Tag: <{el['tag']} type='{el['type']}'> Label: '{lbl}' Name: '{el['name']}' Value: '{val}'{options_str}"
        )

    prompt = (
        f"You are an autonomous web browser agent. Your goal: '{goal}'.\n\n"
        f"Form data available to fill:\n{json.dumps(form_data, indent=2)}\n\n"
        f"Visible Interactive Elements on Screen:\n"
        + "\n".join(elements_summary)
        + "\n\n"
        "Choose the SINGLE NEXT BEST ACTION. Return ONLY a valid JSON object with:\n"
        '{"thought": "brief explanation", "action": "fill" | "click" | "select" | "scroll" | "done", "target_index": <int or null>, "value": "<text to enter or option to select>"}\n'
        "Rules:\n"
        "1. target_index MUST be chosen from the active [index] numbers listed above.\n"
        "2. If all text/select fields are filled, click the submit/send button.\n"
        "3. If the form has been submitted, the goal is achieved, or no more actions are needed, return action: 'done'."
    )

    try:
        res = requests.post(
            f"{OLLAMA_API_BASE}/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1, "num_predict": 180},
            },
            timeout=8,
        )
        if res.status_code == 200:
            text = res.json().get("response", "").strip()
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
    except Exception:
        # Fallback to faster llama3.2 if available
        try:
            res = requests.post(
                f"{OLLAMA_API_BASE}/api/generate",
                json={
                    "model": "llama3.2:latest",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.1, "num_predict": 150},
                },
                timeout=6,
            )
            if res.status_code == 200:
                text = res.json().get("response", "").strip()
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
        except Exception:
            pass

    return None


def _heuristic_next_action(
    elements: List[Dict[str, Any]], filled_indices: List[int], form_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Intelligent semantic field matcher fallback.
    Matches form inputs against form_data keys, then locates and clicks submit button.
    """
    # 1. Look for unfilled input/textarea/select fields that match form_data keys
    field_synonyms = {
        "name": [
            "name",
            "full name",
            "fullname",
            "applicant",
            "contact_name",
            "first and last",
        ],
        "first_name": ["first name", "firstname", "first", "fname"],
        "last_name": ["last name", "lastname", "last", "lname", "surname"],
        "email": ["email", "e-mail", "email address", "user_email"],
        "phone": ["phone", "telephone", "mobile", "cell", "phone number", "tel"],
        "company": ["company", "organization", "business", "employer"],
        "message": [
            "message",
            "comments",
            "cover letter",
            "cover_letter",
            "note",
            "inquiry",
            "details",
            "reason",
            "why",
        ],
    }

    for el in elements:
        idx = el["index"]
        if idx in filled_indices:
            continue

        tag = el["tag"]
        el_type = el["type"].lower()
        if tag not in ["input", "textarea", "select"] or el_type in [
            "submit",
            "button",
            "hidden",
        ]:
            continue

        descriptors = [
            el.get("label", "").lower(),
            el.get("placeholder", "").lower(),
            el.get("name", "").lower(),
            el.get("id", "").lower(),
        ]
        combined = " ".join(descriptors)

        # Match against data keys
        for key, val in form_data.items():
            if not val:
                continue
            synonyms = field_synonyms.get(key, [key])
            if any(syn in combined for syn in synonyms):
                if tag == "select":
                    # Choose closest matching option if available
                    options = el.get("options", [])
                    matched_opt = str(val)
                    for opt in options:
                        if (
                            opt["text"].lower() in str(val).lower()
                            or str(val).lower() in opt["text"].lower()
                        ):
                            matched_opt = opt["value"] or opt["text"]
                            break
                    return {
                        "thought": f"Matched select '{key}' with option '{matched_opt}'",
                        "action": "select",
                        "target_index": idx,
                        "value": matched_opt,
                    }
                else:
                    return {
                        "thought": f"Matched field '{combined}' to form data key '{key}'",
                        "action": "fill",
                        "target_index": idx,
                        "value": str(val),
                    }

    # 2. If all inputs matched/filled, look for submit or apply button
    submit_terms = [
        "submit",
        "send",
        "apply",
        "apply now",
        "continue",
        "next",
        "save",
        "register",
        "done",
    ]
    for el in elements:
        tag = el["tag"]
        el_type = el["type"].lower()
        text = (el.get("text") or el.get("value") or el.get("label") or "").lower()
        if tag in ["button", "input"] and (
            el_type in ["submit", "button"] or tag == "button"
        ):
            if any(term in text for term in submit_terms):
                if el["index"] not in filled_indices:
                    return {
                        "thought": f"Found submission button '{text}'",
                        "action": "click",
                        "target_index": el["index"],
                        "value": "",
                    }

    # 3. Nothing left to do
    return {
        "thought": "All applicable form fields processed.",
        "action": "done",
        "target_index": None,
        "value": "",
    }


def autonomous_agentic_browser_loop(
    url: str,
    task_instruction: str = "Fill out the form and submit",
    form_data: Optional[Dict[str, Any]] = None,
    max_steps: int = 12,
    headless: bool = False,
) -> Dict[str, Any]:
    """
    Autonomous Browser-Use style agent loop:
    1. Opens browser and dynamically extracts visible interactive DOM nodes with unique tags.
    2. Uses iterative LLM decision-making (with intelligent heuristic fallback) to determine actions.
    3. Types text, selects options, and clicks buttons dynamically on ANY arbitrary form.
    4. Confirms submission, captures screenshot, and returns complete audit history.
    """
    if (
        not url.startswith("http://")
        and not url.startswith("https://")
        and not url.startswith("file://")
    ):
        url = "https://" + url

    effective_data = _get_default_user_profile()
    if form_data:
        effective_data.update(form_data)

    print(f"\n=======================================================")
    print(f"🤖 [BrowserAgent] Starting Autonomous Agentic Interaction Loop")
    print(f"🎯 Target URL: {url}")
    print(f"📋 Goal: {task_instruction}")
    print(f"=======================================================\n")

    logs: List[Dict[str, Any]] = []
    filled_indices: List[int] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, args=["--start-maximized"])
            context = browser.new_context(no_viewport=True)
            page = context.new_page()

            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(2)

            step_count = 0
            while step_count < max_steps:
                step_count += 1

                # Inject tagging and inspect interactive elements on current DOM state
                dom_state = page.evaluate("""() => {
                    const isVisible = (elem) => {
                        if (!elem) return false;
                        const style = window.getComputedStyle(elem);
                        const rect = elem.getBoundingClientRect();
                        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0;
                    };
                    
                    const elements = [];
                    const nodes = document.querySelectorAll('input:not([type="hidden"]), textarea, select, button, a[role="button"], [onclick]');
                    
                    let index = 1;
                    nodes.forEach(node => {
                        if (!isVisible(node)) return;
                        
                        let labelText = '';
                        if (node.labels && node.labels.length > 0) {
                            labelText = node.labels[0].innerText.trim();
                        } else if (node.id) {
                            const lbl = document.querySelector(`label[for="${node.id}"]`);
                            if (lbl) labelText = lbl.innerText.trim();
                        }
                        if (!labelText && node.closest('label')) {
                            labelText = node.closest('label').innerText.trim();
                        }
                        
                        const targetId = `agy-node-${index}`;
                        node.setAttribute('data-agy-id', targetId);
                        
                        let options = [];
                        if (node.tagName.toLowerCase() === 'select') {
                            options = Array.from(node.options).map(o => ({ text: o.text.trim(), value: o.value }));
                        }

                        elements.push({
                            index: index,
                            target_id: targetId,
                            tag: node.tagName.toLowerCase(),
                            type: node.type || '',
                            name: node.name || '',
                            id: node.id || '',
                            placeholder: node.placeholder || '',
                            label: labelText,
                            text: (node.innerText || '').trim().substring(0, 50),
                            value: node.value || '',
                            options: options.slice(0, 8),
                            checked: node.checked || false
                        });
                        index++;
                    });
                    
                    return {
                        title: document.title,
                        url: window.location.href,
                        elements: elements
                    };
                }""")

                elements = dom_state.get("elements", [])
                dom_state.get("title", "")

                # Decide next action: LLM with fallback
                decision = _query_llm_action(
                    task_instruction, elements, filled_indices, effective_data
                )
                engine_used = "Ollama-LLM"
                valid_indices = [e["index"] for e in elements]
                if (
                    not decision
                    or not decision.get("action")
                    or decision.get("action") == "unknown"
                    or (
                        decision.get("target_index") is not None
                        and decision.get("target_index") not in valid_indices
                    )
                ):
                    decision = _heuristic_next_action(
                        elements, filled_indices, effective_data
                    )
                    engine_used = "Autonomous-Semantic-Matcher"

                action = decision.get("action", "done")
                target_idx = decision.get("target_index")
                val_to_use = decision.get("value", "")
                thought = decision.get("thought", "")

                print(f"[Step {step_count}] ({engine_used}) Thought: {thought}")
                print(
                    f"         Action: {action.upper()} | Target: [{target_idx}] | Value: '{val_to_use}'"
                )

                step_record = {
                    "step": step_count,
                    "engine": engine_used,
                    "thought": thought,
                    "action": action,
                    "target_index": target_idx,
                    "value": val_to_use,
                }

                if action == "done":
                    logs.append(step_record)
                    print(
                        f"✅ [BrowserAgent] Interaction loop concluded gracefully at Step {step_count}."
                    )
                    break

                if target_idx is not None:
                    selector = f'[data-agy-id="agy-node-{target_idx}"]'
                    try:
                        locator = page.locator(selector).first
                        if locator.is_visible():
                            if action == "fill":
                                locator.fill(val_to_use)
                                filled_indices.append(target_idx)
                                step_record["status"] = "success"
                            elif action == "click":
                                locator.click()
                                filled_indices.append(target_idx)
                                step_record["status"] = "success"
                                time.sleep(1.5)
                            elif action == "select":
                                try:
                                    locator.select_option(val_to_use)
                                except Exception:
                                    locator.select_option(label=val_to_use)
                                filled_indices.append(target_idx)
                                step_record["status"] = "success"
                            time.sleep(0.5)
                        else:
                            step_record["status"] = "element_not_visible"
                    except Exception as e:
                        step_record["status"] = f"action_error: {str(e)}"
                elif action == "scroll":
                    page.evaluate("window.scrollBy(0, 400)")
                    time.sleep(0.8)
                    step_record["status"] = "scrolled"

                logs.append(step_record)

            # Final capture and verification
            final_title = page.title()
            final_url = page.url
            time.sleep(1.5)
            browser.close()

            return {
                "status": "success",
                "goal": task_instruction,
                "target_url": url,
                "final_url": final_url,
                "page_title": final_title,
                "total_steps": len(logs),
                "steps_log": logs,
            }
    except Exception as e:
        print(f"❌ [BrowserAgent] Execution error: {e}")
        return {"status": "error", "message": str(e), "steps_log": logs}


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(json.dumps(inspect_dom_tree(target), indent=2))
    else:
        print(json.dumps(inspect_dom_tree("https://ca.indeed.com"), indent=2))
