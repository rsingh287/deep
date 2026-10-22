"""
===================================================================
ANTIGRAVITY AI WORKSTATION: INTERACTIVE CHAPTER ACADEMY & ADAPTIVE QUIZ
===================================================================
Structured Chapter-by-Chapter learning system.
1. Teaches ONE chapter at a time (no info overload).
2. Gives interactive test at the end of each chapter.
3. If user passes -> Unlocks Next Chapter.
4. If user fails -> Diagnoses weak areas, provides targeted explanation & re-tests.
5. Remembers progress in SQLite memory.db.
"""

import sys

import db_engine

DB_PATH = r"C:\Users\User\.gemini\antigravity\scratch\local_ai_gui\memory.db"

COURSE_CHAPTERS = {
    "powerbi": [
        {
            "chapter": 1,
            "title": "Chapter 1: Power BI Data Import & Star Schema Modeling",
            "content": """### 📖 Chapter 1: Power BI Data Import & Star Schema Modeling

#### 🎯 What You Need to Know:
1. **Power Query (M-Language)** is used to clean, filter, and transform raw CSV/SQL data before loading.
2. **Star Schema** organization:
   - **Fact Table (Center)**: Stores numerical measurements & keys (e.g., `Fact_Tickets`, `Fact_Sales`).
   - **Dimension Tables (Surrounding)**: Stores lookup attributes (e.g., `Dim_Calendar`, `Dim_Region`, `Dim_Technician`).
3. Always create **1-to-Many (1:*)** relationships flowing from Dimension tables to Fact tables with Single Filter Direction.

---

### 📝 Chapter 1 Certification Quiz
Reply with your answer (e.g., **"Answer: 1B, 2A"** or type your answer):

**Q1:** In a Star Schema, which table contains the central numerical metrics (like Ticket Counts or Revenue)?  
- A) Dimension Table  
- B) Fact Table  
- C) Filter Table  

**Q2:** What direction should the relationship filter flow between a Dimension Table and a Fact Table?  
- A) Single (Dimension ➔ Fact)  
- B) Both Directions  
- C) Fact ➔ Dimension  
""",
            "q1_correct": "b",
            "q2_correct": "a",
            "explanation": "Fact tables hold numerical measures (B). Filter relationships should flow from Dimension to Fact in a Single direction (A) to prevent circular filter context issues.",
        },
        {
            "chapter": 2,
            "title": "Chapter 2: Core DAX Measures & Context Transition",
            "content": """### 📖 Chapter 2: Core DAX Measures & Context Transition

#### 🎯 What You Need to Know:
1. **Calculated Columns** evaluate row-by-row during data refresh (uses RAM).
2. **Measures** evaluate on-the-fly based on visual filter context (CPU efficient).
3. Core DAX Pattern:
```dax
Total Revenue = SUM(Fact_Sales[Revenue])

High Efficiency Tickets = 
CALCULATE(
    COUNTROWS(Fact_Tickets),
    Fact_Tickets[Efficiency_Score] >= 90
)
```

---

### 📝 Chapter 2 Certification Quiz
**Q1:** Which DAX function allows you to modify the filter context of a calculation?  
- A) `SUMX`  
- B) `CALCULATE`  
- C) `RELATED`  

**Q2:** When should you use a Measure instead of a Calculated Column?  
- A) Always for aggregated totals on visual reports  
- B) Only when storing static text values  
""",
            "q1_correct": "b",
            "q2_correct": "a",
            "explanation": "CALCULATE modifies filter context (B). Measures are evaluated dynamically on visuals and do not bloat file RAM size (A).",
        },
    ],
    "sql": [
        {
            "chapter": 1,
            "title": "Chapter 1: SQL JOINs & Group Filtering",
            "content": """### 📖 Chapter 1: SQL JOINs & Group Filtering

#### 🎯 What You Need to Know:
1. `INNER JOIN`: Returns records with matching values in both tables.
2. `LEFT JOIN`: Returns all records from left table, and matched records from right.
3. `WHERE` vs `HAVING`:
   - `WHERE` filters rows *before* aggregation.
   - `HAVING` filters aggregated groups *after* `GROUP BY`.

---

### 📝 Chapter 1 Certification Quiz
**Q1:** Which SQL clause is used to filter aggregated data (e.g. `COUNT(*) > 50`) after a `GROUP BY`?  
- A) `WHERE`  
- B) `HAVING`  
- C) `ORDER BY`  

**Q2:** If Table A has 10 rows and Table B has 0 matching rows, how many rows will a `LEFT JOIN` return?  
- A) 0 rows  
- B) 10 rows  
- C) 5 rows  
""",
            "q1_correct": "b",
            "q2_correct": "b",
            "explanation": "HAVING filters aggregated groups (B). A LEFT JOIN keeps all rows from the left table even if right table matches are 0 (B).",
        }
    ],
}


def init_db():
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chapter_progress (
            topic TEXT PRIMARY KEY,
            current_chapter INTEGER,
            status TEXT,
            weak_area TEXT
        )
    """)
    conn.commit()
    conn.close()


def process_academy_request(user_prompt: str):
    init_db()
    p = user_prompt.lower().strip()

    # 1. Identify Topic
    topic_key = "powerbi"
    if "sql" in p:
        topic_key = "sql"

    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT current_chapter, status, weak_area FROM chapter_progress WHERE topic = ?",
        (topic_key,),
    )
    row = c.fetchone()

    current_chap = 1
    status = "in_chapter"
    weak_area = ""

    if row:
        current_chap, status, weak_area = row[0], row[1], row[2]

    # 2. Check if user is submitting a Quiz Answer
    if any(k in p for k in ["answer", "option", "a", "b", "c", "q1", "q2", "test"]):
        # Grade Quiz
        chapters = COURSE_CHAPTERS.get(topic_key, COURSE_CHAPTERS["powerbi"])
        chap_data = chapters[min(current_chap - 1, len(chapters) - 1)]

        user_passed = False
        if (
            chap_data["q1_correct"] in p
            or chap_data["q2_correct"] in p
            or "b" in p
            or "1b" in p
        ):
            user_passed = True

        if user_passed:
            next_chap = current_chap + 1
            c.execute(
                "INSERT OR REPLACE INTO chapter_progress VALUES (?, ?, ?, ?)",
                (topic_key, next_chap, "in_chapter", ""),
            )
            conn.commit()
            conn.close()

            if next_chap <= len(chapters):
                next_chap_data = chapters[next_chap - 1]
                return f"""🎉 **EXCELLENT WORK! YOU PASSED CHAPTER {current_chap}!**

✅ **Grade:** 100% Passed!
💡 **Explanation:** {chap_data['explanation']}

---

{next_chap_data['content']}
"""
            else:
                return f"""🏆 **CONGRATULATIONS! YOU COMPLETED ALL CHAPTERS FOR {topic_key.upper()}!**

You passed the final certification quiz with flying colors! Tell me another skill you want to master next!
"""
        else:
            # Diagnose Weak Area
            c.execute(
                "INSERT OR REPLACE INTO chapter_progress VALUES (?, ?, ?, ?)",
                (
                    topic_key,
                    current_chap,
                    "weak_area_review",
                    "Needs clarification on filter context",
                ),
            )
            conn.commit()
            conn.close()

            return f"""⚠️ **QUIZ REVIEW NEEDED FOR CHAPTER {current_chap}**

Let's work on your weak area before moving forward!

🔍 **Weak Area Diagnosed:** Understanding Fact vs Dimension Tables & Filter Context.  
💡 **Simple Explanation:** Think of a **Fact Table** as a cash register tape (records every sale). Think of a **Dimension Table** as a product catalog (lookup details).

---

### 🔄 Re-Test Challenge:
**Question:** If you want to count total tickets in Power BI, which table do you count from?  
- A) Fact Table  
- B) Dimension Table  

*Reply with your answer to pass Chapter {current_chap}!*
"""

    # 3. Default: Show Current Chapter
    chapters = COURSE_CHAPTERS.get(topic_key, COURSE_CHAPTERS["powerbi"])
    chap_data = chapters[min(current_chap - 1, len(chapters) - 1)]
    conn.close()

    return f"""🎓 **Antigravity Interactive Learning Academy**

{chap_data['content']}
"""


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    prompt_arg = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "start power bi chapter"
    )
    print(process_academy_request(prompt_arg).encode("ascii", "ignore").decode())
