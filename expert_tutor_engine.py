"""
===================================================================
ANTIGRAVITY AI WORKSTATION: EXPERT TUTOR & MASTER SKILL ENGINE
===================================================================
Provides expert-level, step-by-step interactive teaching, hands-on labs,
code exercises, interview prep, and quizzes across IT, Telecom, Data Analytics,
Power BI, Python DOM Automation, and AI Engineering.
"""

import sys

TUTORIAL_CURRICULUM = {
    "powerbi": {
        "title": "⚡ Master Power BI & DAX Data Analytics (Expert Level)",
        "modules": [
            "Module 1: Data Import & Transformation (Power Query / M-Language)",
            "Module 2: Relational Data Modeling (Star Schema & Snowflake Schema)",
            "Module 3: Advanced DAX Calculations (CALCULATE, SUMX, FILTER, Time Intelligence)",
            "Module 4: Executive Dashboard UI/UX Design & RLS (Row-Level Security)",
        ],
        "lesson": """### ⚡ Lesson 1: Star Schema & Core DAX Formulas

#### 🎯 Key Concept:
In Power BI, always organize your data into a **Star Schema** with 1 **Fact Table** (transactions/tickets) in the center connected to **Dimension Tables** (Calendar, Region, Technician).

#### 💻 Hands-On DAX Code Example:
```dax
// 1. Total Tickets Measure
Total Tickets = COUNTROWS('Fact_Tickets')

// 2. High Priority Resolution Rate (Filtered Context)
High Priority Resolution % = 
DIVIDE(
    CALCULATE([Total Tickets], 'Fact_Tickets'[Priority] = "High", 'Fact_Tickets'[Status] = "Resolved"),
    CALCULATE([Total Tickets], 'Fact_Tickets'[Priority] = "High"),
    0
)
```

#### 💡 Pro Tip for Interviews:
When asked *"What is the difference between EARLIER and CALCULATE in DAX?"*, explain that `CALCULATE` modifies filter context using context transition, while `EARLIER` accesses outer row context before context transition.
""",
    },
    "sql": {
        "title": "🗄️ Master SQL & Enterprise Database Querying (Expert Level)",
        "modules": [
            "Module 1: DDL/DML Fundamentals & Indexing Strategies",
            "Module 2: Complex JOINs, GROUP BY & Aggregation Optimizations",
            "Module 3: Advanced Window Functions (ROW_NUMBER, RANK, LEAD, LAG, PARTITION BY)",
            "Module 4: Database Administration, Stored Procedures & Query Tuning",
        ],
        "lesson": """### 🗄️ Lesson 1: Advanced Window Functions (`PARTITION BY`)

#### 🎯 Key Concept:
Window functions perform calculations across a set of table rows related to the current row without collapsing rows into a single output row.

#### 💻 Hands-On SQL Code Example:
```sql
-- Find the top performing Technician in each Region based on resolved tickets
WITH RankedTechs AS (
    SELECT 
        technician_name,
        region_name,
        tickets_resolved,
        ROW_NUMBER() OVER (
            PARTITION BY region_name 
            ORDER BY tickets_resolved DESC
        ) AS rank_in_region
    FROM telecom_it_support_logs
)
SELECT technician_name, region_name, tickets_resolved
FROM RankedTechs
WHERE rank_in_region = 1;
```

#### 🧠 Interview Practice Challenge:
Write a query to calculate a 7-day moving average of ticket resolutions using `AVG(...) OVER (ORDER BY date_col ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.
""",
    },
    "fiber": {
        "title": "📡 Master Telecommunications, Fiber Optics & OTDR Testing (Expert Level)",
        "modules": [
            "Module 1: Optical Fiber Physics (Single-Mode 1310/1550nm vs Multi-Mode)",
            "Module 2: Fusion Splicing & Fiber Enclosure Preparation",
            "Module 3: OTDR Tracing (Event Loss, Splice Loss, Reflectance & Break Location)",
            "Module 4: Structured Cabling (Cat6A, RJ45 Pinouts T568A/B, Cable Certification)",
        ],
        "lesson": """### 📡 Lesson 1: Reading OTDR Tracing Reports & Event Loss

#### 🎯 Key Concept:
An **OTDR (Optical Time-Domain Reflectometer)** sends light pulses down the fiber strand and measures Fresnel reflections and Rayleigh backscattering.

#### 📊 Event Breakdown on OTDR Trace Graph:
1. **Initial Dead Zone**: High reflective peak caused by front panel connector connection.
2. **Splice Loss Event**: Non-reflective step down on the trace curve (acceptable splice loss: `< 0.05 dB`).
3. **Connector Event**: Reflective spike with downward step (acceptable connector loss: `< 0.3 dB`).
4. **Fiber Break**: Sudden sharp drop off to noise floor at exact distance marker (e.g. at 4.25 km).

#### 💡 Bell Field Tech Rule:
Always clean fiber end-faces with 99.9% Isopropyl Alcohol and lint-free wipes before inserting into OTDR ports to prevent connector degradation.
""",
    },
    "automation": {
        "title": "🤖 Master Python Playwright & DOM Automation (Expert Level)",
        "modules": [
            "Module 1: DOM Selectors, XPaths & Shadow DOM Navigation",
            "Module 2: Asynchronous Playwright & Headless Browser Automation",
            "Module 3: Form Auto-Filling, File Uploads & Captcha Bypass Patterns",
            "Module 4: Web Scraping, API Hooking & Database Integration",
        ],
        "lesson": """### 🤖 Lesson 1: Asynchronous Playwright DOM Manipulation

#### 🎯 Key Concept:
Playwright allows you to script headless Chromium browsers to interact with web pages exactly like a human user.

#### 💻 Hands-On Python Code Example:
```python
import asyncio
from playwright.async_api import async_playwright

async def auto_fill_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://ca.indeed.com")
        
        # 1. Target DOM Node via CSS Selector
        await page.fill('input[name="q"]', 'IT Support Specialist')
        await page.fill('input[name="l"]', 'Mississauga, ON')
        
        # 2. Click Search Button Node
        await page.click('button[type="submit"]')
        
        # 3. Wait for DOM state transition
        await page.wait_for_selector('.job_seen_beacon')
        print("DOM element loaded successfully!")
        await browser.close()

asyncio.run(auto_fill_form())
```

#### ❓ Hands-On Challenge:
Modify the selector above to use `page.locator('text="Apply Now"')` to trigger autonomous job applications!
""",
    },
}


def generate_expert_tutorial(topic_prompt: str):
    """Generates an expert-level, step-by-step tutorial based on user requested skill."""
    p = topic_prompt.lower()

    selected_key = "powerbi"
    if "sql" in p or "database" in p or "query" in p:
        selected_key = "sql"
    elif "fiber" in p or "otdr" in p or "telecom" in p or "cabling" in p:
        selected_key = "fiber"
    elif (
        "automation" in p
        or "playwright" in p
        or "dom" in p
        or "python" in p
        or "scrape" in p
    ):
        selected_key = "automation"

    data = TUTORIAL_CURRICULUM[selected_key]

    modules_md = "\n".join([f"- **{m}**" for m in data["modules"]])

    return f"""🎓 **Antigravity AI Expert Academy**

# {data['title']}

## 📚 Master Curriculum Modules:
{modules_md}

---

{data['lesson']}

---

### 🚀 Next Steps & Practice:
Tell me: **"give me practice test for {selected_key}"** or **"next lesson"** to continue your expert training!
"""


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    test_topic = sys.argv[1] if len(sys.argv) > 1 else "teach me power bi"
    print(generate_expert_tutorial(test_topic))
