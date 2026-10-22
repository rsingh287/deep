import os

import db_engine


def populate_master_skills():
    os.path.join(os.getcwd(), "memory.db")
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS facts (concept TEXT PRIMARY KEY, facts TEXT)")

    new_skills = [
        (
            "PERSONAL_ASSISTANCE_SKILL",
            "Expert Personal Assistant: Organizes daily schedules, manages tasks, automates PC workflows, handles email drafts, manages reminders, and provides seamless bilingual support in Punjabi (ਪੰਜਾਬੀ) and English.",
        ),
        (
            "FINANCIAL_ASSISTANCE_SKILL",
            "Expert Financial Advisor & Analyst: Performs financial modeling, budget planning, expense tracking, investment ROI analysis, stock market analytics, cryptocurrency evaluation, and risk metric calculations (Sharpe Ratio, VaR).",
        ),
        (
            "TECHNICAL_ASSISTANCE_SKILL",
            "Master Technical & Embedded Engineer: Embedded C firmware development (PIC18F85K22 / XC8), system diagnostics, Windows RPA automation, PowerShell/Bash scripting, API design, and network security auditing.",
        ),
        (
            "AI_DATA_SCIENCE_SKILL",
            "Lead AI & Data Science Engineer: Builds PyTorch/TensorFlow ML pipelines, LLM fine-tuning, Hugging Face model deployment, RAG vector search, NLP pipelines, neural networks, and model performance benchmarking.",
        ),
        (
            "DATA_ANALYST_SKILL",
            "Senior Data Analyst: Expert in pandas, NumPy, SQL query optimization, Exploratory Data Analysis (EDA), statistical modeling, interactive visualization (Plotly/Seaborn), and executive KPI business intelligence dashboards.",
        ),
    ]

    c.executemany(
        "INSERT OR REPLACE INTO facts (concept, facts) VALUES (?, ?)", new_skills
    )
    conn.commit()

    # Query all facts to verify
    c.execute("SELECT concept, facts FROM facts")
    rows = c.fetchall()
    conn.close()

    print("------------------------------------------------------------")
    print(f"SUCCESSFULLY STORED {len(rows)} MASTER SKILLS IN MEMORY DB:")
    print("------------------------------------------------------------")
    for r in rows:
        print(f"• [{r[0]}]: {r[1][:90]}...")
    print("------------------------------------------------------------")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    populate_master_skills()
