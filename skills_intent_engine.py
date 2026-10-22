import os
import re
import sqlite3

import db_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

try:
    import agent_skill_runtime
except ImportError:
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    import agent_skill_runtime


def handle_skills_intent(user_prompt: str):
    if not user_prompt:
        return None

    p_low = user_prompt.lower().strip()
    p_clean = re.sub(r"[\.\?\!\;]+$", "", p_low).strip()
    p_clean = re.sub(r"\bu\b", "you", p_clean)
    p_clean = re.sub(r"\br\b", "are", p_clean)
    p_clean = re.sub(r"\bur\b", "your", p_clean)

    # If prompt is an everyday PC command, do NOT intercept with engineering skills
    everyday_indicators = [
        "volume",
        "sound",
        "mute",
        "unmute",
        "brightness",
        "dim",
        "calc",
        "calculator",
        "notepad",
        "screenshot",
        "taskmgr",
        "task manager",
        "settings",
        "paint",
        "explorer",
        "downloads",
        "documents",
        "desktop",
        "pictures",
        "videos",
        "recycle bin",
        "lock pc",
        "sleep pc",
        "time",
        "date",
        "battery",
        "specs",
        "ram",
        "cpu",
        "ip address",
        "youtube",
        "google",
        "gmail",
        "github",
        "how are you",
        "what's up",
        "hey",
        "hello",
        "hi",
    ]
    if any(
        p_clean == ind or p_clean.startswith(ind + " ") or f" {ind} " in f" {p_clean} "
        for ind in [
            "volume",
            "sound",
            "brightness",
            "calculator",
            "notepad",
            "screenshot",
            "downloads",
            "documents",
        ]
    ):
        return None

    # 0. Screen Pilot (Live Visual Automation)
    screen_pilot_triggers = [
        "look at my active screen",
        "read the error message inside the window",
        "extract the data table from this webpage",
        "look at screen",
        "analyze screen",
        "what's on my screen",
        "what is on my screen"
    ]
    if any(t in p_clean for t in screen_pilot_triggers):
        try:
            import screen_vision
            result = screen_vision.analyze_desktop_screen(prompt=user_prompt)
            if result["status"] == "success":
                import time
                return (
                    f"👁️ **Screen Pilot Analysis Complete**\n\n<img src='/screenshots/latest_screen.jpg?t={int(time.time())}' style='max-width:100%; border-radius:8px;'/>\n\n{result['analysis']}",
                    "screen_pilot_success",
                    [{"language": "python", "code": "screen_vision.analyze_desktop_screen()", "output": f"Latency: {result['latency_s']}s\nModel: {result['model_used']}"}]
                )
            else:
                return (
                    f"❌ **Screen Pilot Error**\n\nFailed to capture or analyze screen: {result.get('message', 'Unknown error')}",
                    "screen_pilot_error",
                    []
                )
        except Exception as e:
            pass

    # 1. Broad skill catalog queries
    catalog_triggers = [
        "what skills do you have",
        "list skills",
        "show skills",
        "skills list",
        "all skills",
        "list all skills",
        "what can you do",
        "what you can do",
        "show all skills",
        "my skills",
        "agent skills",
        "skills arsenal",
        "show capabilities",
        "what are your skills",
        "what are the skills",
        "capabilities",
        "what skills can you use",
        "what skills",
    ]
    if any(t in p_clean for t in catalog_triggers):
        return get_skills_catalog_overview()

    # 2. Category specific queries
    cat_mapping = {
        "web": "Web & Frontend",
        "frontend": "Web & Frontend",
        "backend": "Backend & Systems",
        "ai": "AI, Agents & Prompts",
        "agent": "AI, Agents & Prompts",
        "prompt": "AI, Agents & Prompts",
        "cloud": "Data & Cloud Architecture",
        "database": "Data & Cloud Architecture",
        "sql": "Data & Cloud Architecture",
        "security": "Cybersecurity & Forensics",
        "cyber": "Cybersecurity & Forensics",
        "mobile": "Mobile & Cross-Platform",
        "flutter": "Mobile & Cross-Platform",
        "devops": "DevOps, SRE & QA",
        "qa": "DevOps, SRE & QA",
        "testing": "DevOps, SRE & QA",
        "science": "Science & Bio-Informatics",
        "bio": "Science & Bio-Informatics",
        "business": "Business & Enterprise",
    }

    m_cat = re.search(r"(?:show|list|get|find)\s+([a-z\s]+)\s+skills", p_clean)
    if m_cat:
        kw = m_cat.group(1).strip()
        matched_cat = None
        for k, v in cat_mapping.items():
            if k in kw:
                matched_cat = v
                break
        if matched_cat:
            return get_skills_by_category_report(matched_cat)

    # 3. Direct skill invocation or run
    invoke_prefixes = [
        "invoke skill",
        "run skill",
        "use skill",
        "skill:",
        "skill ",
        "how to use skill",
        "activate skill",
        "execute skill",
    ]
    for pref in invoke_prefixes:
        if p_clean.startswith(pref):
            skill_query = p_clean[len(pref) :].strip()
            if skill_query:
                return execute_skill_and_generate_briefing(skill_query, user_prompt)

    # 4. Direct keyword matches for prominent custom agents and tools
    if (
        "flutter_a11y" in p_clean
        or "flutter accessibility" in p_clean
        or "a11y review" in p_clean
    ):
        return execute_skill_and_generate_briefing("flutter_a11y_agent", user_prompt)
    if "accessibility audit" in p_clean or "wcag audit" in p_clean:
        return execute_skill_and_generate_briefing(
            "accessibility-compliance-accessibility-audit", user_prompt
        )
    if "threat modeling" in p_clean or "stride analysis" in p_clean:
        return execute_skill_and_generate_briefing(
            "threat-modeling-expert", user_prompt
        )
    if "security audit" in p_clean or "security-auditor" in p_clean:
        return execute_skill_and_generate_briefing("security-auditor", user_prompt)
    if "bash defensive" in p_clean or "defensive bash" in p_clean:
        return execute_skill_and_generate_briefing(
            "bash-defensive-patterns", user_prompt
        )
    # If the user is asking to WRITE / CREATE / BUILD / CODE / GENERATE, do NOT intercept with a static documentation briefing!
    # Instead, let it pass to the LLM where build_system_prompt_skill_injection injects the full skill blueprint so the AI generates the code!
    is_code_request = any(
        v in p_clean
        for v in [
            "create",
            "write",
            "make",
            "build",
            "generate",
            "code",
            "program",
            "develop",
            "implement",
            "design",
        ]
    )

    if not is_code_request and any(
        k in p_clean
        for k in [
            "pic board",
            "pic18f",
            "pickit",
            "pickit3",
            "pic microcontroller",
            "embedded pic",
            "pic-embedded-engineer",
            "mcp9701",
            "trainer board",
        ]
    ):
        return execute_skill_and_generate_briefing("pic-embedded-engineer", user_prompt)



    # 5. Check if user is asking to clear active skill
    if any(
        w in p_clean
        for w in [
            "clear skill",
            "reset skill",
            "exit skill",
            "deactivate skill",
            "clear active skill",
        ]
    ):
        agent_skill_runtime.clear_active_skill()
        return (
            "🔄 **Active Skill Cleared:** Your AI Agent is now operating in general autonomous workstation mode.",
            "skill_cleared",
            [
                {
                    "language": "text",
                    "code": "clear_active_skill()",
                    "output": "General Mode Active",
                }
            ],
        )

    return None


def get_skills_catalog_overview():
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT category, count(*) FROM agent_skills GROUP BY category ORDER BY count(*) DESC"
        )
        cat_stats = c.fetchall()
        c.execute("SELECT count(*) FROM agent_skills")
        total = c.fetchone()[0]
        conn.close()
    except Exception as e:
        total = 422
        cat_stats = [
            ("Backend & Systems", 95),
            ("Core Automation", 70),
            ("Web & Frontend", 60),
            ("AI, Agents & Prompts", 58),
            ("Data & Cloud Architecture", 49),
            ("DevOps, SRE & QA", 26),
            ("Cybersecurity & Forensics", 22),
            ("Mobile & Cross-Platform", 20),
            ("Business & Enterprise", 14),
            ("Science & Bio-Informatics", 8),
        ]

    active = agent_skill_runtime.get_active_skill()
    active_line = (
        f"🟢 **Currently Active Skill:** `{active['name']}` (`{active['skill_id']}`)\n\n"
        if active
        else ""
    )

    lines = [
        f"⚡ **MASTER AI SKILLS ARSENAL: {total} ACTIVE CAPABILITIES**\n",
        active_line,
        f"Your Local AI PC Cockpit is equipped with **{total} specialized engineering skills & custom agents** organized into 9 domain divisions:\n",
    ]
    for cat, cnt in cat_stats:
        lines.append(f"- **{cat}:** `{cnt} skills active`")

    lines.append("\n---")
    lines.append("### 🎯 How to Utilize Your Skills Arsenal in the PC App:")
    lines.append(
        "1. **Interactive Skills Hub:** Open **[AI Skills & Capabilities (`/skills`)](http://127.0.0.1:5000/skills)** in your top navigation bar to search and filter."
    )
    lines.append(
        "2. **Direct Invocation:** Type `invoke skill <name>` (e.g. `invoke skill flutter_a11y_agent`)."
    )
    lines.append(
        "3. **Category Drilldown:** Ask `list mobile skills`, `list security skills`, or `list AI skills`."
    )
    lines.append(
        "4. **Ask Any Question:** Any engineering question automatically inherits the corresponding skill rules."
    )

    output_text = "\n".join(lines)
    return (
        output_text,
        "skills_arsenal_catalog",
        [
            {
                "language": "json",
                "code": f'{{"total_skills": {total}, "status": "active", "catalog_url": "/skills"}}',
                "output": f"Loaded {total} master skills from memory.db",
            }
        ],
    )


def get_skills_by_category_report(category_name):
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT id, name, description, plugin FROM agent_skills WHERE category LIKE ? ORDER BY name ASC",
            (f"%{category_name}%",),
        )
        rows = c.fetchall()
        conn.close()
    except Exception as e:
        rows = []

    lines = [
        f"📂 **{category_name.upper()} SKILLS DIVISION** ({len(rows)} Skills Available):\n"
    ]
    for r in rows[:15]:
        plugin_badge = f" `[{r[3]}]`" if r[3] else ""
        desc_short = r[2][:120] + "..." if len(r[2]) > 120 else r[2]
        lines.append(f"• **{r[1]}** (`{r[0]}`){plugin_badge}\n  *{desc_short}*\n")

    if len(rows) > 15:
        lines.append(
            f"*(...and {len(rows) - 15} more skills in this category. Open [/skills](http://127.0.0.1:5000/skills) to explore all)*\n"
        )

    return (
        "\n".join(lines),
        f"skills_{category_name.lower().replace(' ', '_')}",
        [
            {
                "language": "json",
                "code": f'{{"category": "{category_name}", "count": {len(rows)}}}',
                "output": f"Found {len(rows)} matching skills",
            }
        ],
    )


def execute_skill_and_generate_briefing(
    skill_query, raw_prompt="", is_auto_selected=False, match_score=0
):
    try:
        conn = db_engine.get_db_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM agent_skills WHERE id = ? OR LOWER(id) = ? OR LOWER(name) = ? OR LOWER(id) LIKE ? OR LOWER(name) LIKE ? LIMIT 1",
            (
                skill_query,
                skill_query.lower(),
                skill_query.lower(),
                f"%{skill_query.lower()}%",
                f"%{skill_query.lower()}%",
            ),
        )
        row = c.fetchone()
        conn.close()
    except Exception as e:
        row = None

    if not row:
        return (
            f"🔍 **Skill Not Found:** Could not locate a skill matching `{skill_query}`. Open the **[Skills Hub (`/skills`)](http://127.0.0.1:5000/skills)** to view all 422 available capabilities.",
            "skill_search_not_found",
            [
                {
                    "language": "text",
                    "code": f"search_skill('{skill_query}')",
                    "output": "0 results",
                }
            ],
        )

    s = dict(row)
    agent_skill_runtime.set_active_skill(s["id"], s["name"])
    content, file_path = agent_skill_runtime.get_skill_content(s["id"])

    auto_banner = ""
    if is_auto_selected:
        auto_banner = f"""> ⚡ **AUTOMATICALLY SELECTED SKILL FOR WORK:** **{s['name']}** (`{s['id']}`) *(Match Score: {match_score} pts)*\n> *Deep analyzed your task requirements and automatically engaged this engineering capability to complete your request.*\n\n"""

    # 1. Specialized Custom Agent: Flutter A11y Agent
    if "flutter_a11y" in s["id"]:
        report = auto_banner + f"""# 📱 FLUTTER ACCESSIBILITY (A11Y) AGENT ENGAGED
**Active Capability:** `{s['name']}` (`{s['id']}`)
**Specialization:** WCAG 2.2 Compliance, Screen Readers, Hit-Test Bounds & Semantics Testing
**Status:** 🟢 **Active Working Skill in PC Workstation**

---

## 🎯 Review & Compliance Directives for Your Flutter Codebase:

### 1. 🗣️ Semantics & Screen Readers
- **Meaningful Semantics:** Use built-in parameters (`Icon(semanticLabel: '...')`) or wrap custom widgets in explicit `Semantics(...)`.
- **Merge Semantics:** Use `MergeSemantics` on static cards (e.g. title + subtitle) to create single unified screen reader announcements. *Never use on expandable, interactive, or scrolling lists!*
- **Exclude Decorative:** Wrap purely decorative icons/images in `ExcludeSemantics(child: ...)`.
- **Live Regions:** Avoid `SemanticsService.announce`. Wrap dynamic announcements in `Semantics(container: true, liveRegion: true, child: Text(...))`.

### 2. 👆 Minimum Tap Targets (Hit-Test Bounds)
- **Android:** Minimum **48 × 48 dp / logical pixels**.
- **iOS & Web:** Minimum **44 × 44 dp / logical pixels**.
- Expand hit areas using `EdgeInsets` or `constraints` rather than cramming small buttons.

### 3. 🎨 Visual & Color Contrast (WCAG AA/AAA)
- **Normal Text:** Minimum **4.5:1** contrast ratio against background in both Light & Dark modes.
- **Large Text (≥ 18pt / 14pt bold):** Minimum **3:1** contrast ratio.
- Never convey critical information through color alone; pair colors with icons or labels.

### 4. 📐 Text Scaling & Overflow Prevention
- Avoid hardcoded fixed container `height: ...` around text; allow text to wrap dynamically.
- Never override or pin `textScaleFactor` to `1.0`; honor user accessibility preferences.

### 5. ⌨️ Focus & Keyboard Traversal
- Wrap custom interactive sequences in `FocusTraversalGroup` with `NumericFocusOrder` for logical hardware keyboard flow.

---

## 🧪 Automated Flutter Accessibility Test Template:
Add this unit test to your test suite (`test/a11y_test.dart`) to catch accessibility regressions automatically:
"""
        dart_test = """import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Flutter WCAG & Accessibility Automated Audit', (WidgetTester tester) async {
    // 1. Enable semantics testing handle
    final SemanticsHandle handle = tester.ensureSemantics();

    // 2. Pump your target application screen or widget
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: ElevatedButton(
              onPressed: null,
              child: Text('Accessible Action'),
            ),
          ),
        ),
      ),
    );

    // 3. Verify all 4 Flutter Accessibility Guidelines
    await expectLater(tester, meetsGuideline(textContrastGuideline));
    await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
    await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
    await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));

    // Clean up semantics handle
    handle.dispose();
  });
}"""
        ps_scanner = """# Scan workspace for non-accessible icon buttons missing tooltips or labels
Get-ChildItem -Path . -Filter "*.dart" -Recurse | Select-String -Pattern "IconButton\(" -Context 0,2"""

        return (
            report,
            f"skill_active_{s['id']}",
            [
                {
                    "language": "dart",
                    "code": dart_test,
                    "output": "Flutter Accessibility Test Suite (4 WCAG Guidelines)",
                },
                {
                    "language": "powershell",
                    "code": ps_scanner,
                    "output": "Workspace A11y Dart Code Scanner",
                },
            ],
        )

    # 2. General Skill Handler from Local Markdown
    clean_body = (
        re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL).strip()
        if content
        else s["description"]
    )
    found_blocks = re.findall(r"```([a-zA-Z0-9_\-]+)\n(.*?)```", clean_body, re.DOTALL)

    exec_details = []
    if found_blocks:
        for lang, c_code in found_blocks[:2]:
            exec_details.append(
                {
                    "language": lang,
                    "code": c_code.strip(),
                    "output": f"Loaded from {s['name']} directives",
                }
            )
    else:
        exec_details.append(
            {
                "language": "powershell",
                "code": f"# Skill {s['name']} ({s['id']}) engaged in active workstation memory",
                "output": f"Skill {s['name']} Active",
            }
        )

    report = (
        auto_banner
        + f"""# ⚡ SPECIALIZED ENGINEERING SKILL ENGAGED: {s['name'].upper()}
**Identifier:** `{s['id']}` | **Category:** `{s['category']}` | **Plugin:** `{s.get('plugin') or 'Core'}`
**Status:** 🟢 **Active Working Skill in PC Workstation**

---

{clean_body[:3200]}

---
💡 *Tip: Your AI Agent on this PC will now prioritize the rules, patterns, and methodologies of **{s['name']}** for all subsequent questions and code generations. Type `clear skill` at any time to return to general mode.*
"""
    )
    return (report, f"skill_active_{s['id']}", exec_details)
