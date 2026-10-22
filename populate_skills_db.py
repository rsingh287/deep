import json
import os

import db_engine


def populate_all_skills():
    db_path = os.path.join(os.path.dirname(__file__), "memory.db")
    registry_path = os.path.join(
        os.path.dirname(__file__), "master_skills_registry.json"
    )

    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} not found.")
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        skills = json.load(f)

    conn = db_engine.get_db_connection()
    cursor = conn.cursor()

    # Create agent_skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_skills (
        id TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        plugin TEXT,
        scope TEXT,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Also ensure facts table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concept TEXT UNIQUE,
        facts TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert or replace skills
    inserted = 0
    for s in skills:
        cursor.execute(
            """
        INSERT OR REPLACE INTO agent_skills (id, name, category, plugin, scope, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                s["id"],
                s["name"],
                s["category"],
                s.get("plugin"),
                s.get("scope", "Global"),
                s["description"],
            ),
        )
        inserted += 1

    # Ingest overview fact into facts table
    summary_fact = (
        f"Antigravity Local AI PC Cockpit is endowed with a Master AI Skills Arsenal of {inserted} specialized skills "
        f"and custom agents across 9 core domains: Web & Frontend, Backend & Systems, AI & Agents, Data & Cloud Architecture, "
        f"Cybersecurity & Forensics, Mobile & Cross-Platform (Flutter/iOS/Android), DevOps/SRE/QA, Bioinformatics & Science, and Business Intelligence."
    )
    cursor.execute(
        """
    INSERT OR REPLACE INTO facts (concept, facts)
    VALUES (?, ?)
    """,
        ("MASTER_AI_SKILLS_ARSENAL", summary_fact),
    )

    conn.commit()
    conn.close()
    print(
        f"Successfully populated {inserted} skills into {db_path} agent_skills table!"
    )


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    populate_all_skills()
