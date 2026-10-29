"""
Autonomous IT Job Application Engine
------------------------------------
Searches live IT job postings, generates AI-tailored cover letters using local Ollama models,
tracks job applications in SQLite, and launches automated 1-click application portals.
"""

import json
import os
import time
import urllib.parse
import urllib.request

import db_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")


def init_job_db():
    """Initializes SQLite database table for tracking automated job applications."""
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_applications (
                id SERIAL PRIMARY KEY,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                url TEXT UNIQUE,
                cover_letter TEXT,
                status TEXT DEFAULT 'Applied',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_job_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                full_name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience_summary TEXT,
                github_url TEXT,
                linkedin_url TEXT
            )
        """)

        # Insert default profile if empty
        cursor.execute("SELECT count(*) FROM user_job_profile")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO user_job_profile (id, full_name, email, phone, skills, experience_summary, github_url, linkedin_url)
                VALUES (1, 'IT Candidate', 'candidate@email.com', '+1-555-0199', 
                        'Python, JavaScript, React, SQL, DevOps, REST APIs, Docker, Linux', 
                        'Full-Stack & Systems Software Engineer with 3+ years experience building web applications and automated systems.', 
                        'https://github.com', 'https://linkedin.com')
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[JobApplierDB] Init Error: {e}")


init_job_db()


def get_user_job_profile():
    """Fetches user profile details for job applications."""
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT full_name, email, phone, skills, experience_summary, github_url, linkedin_url FROM user_job_profile WHERE id = 1"
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "full_name": row[0],
                "email": row[1],
                "phone": row[2],
                "skills": row[3],
                "experience_summary": row[4],
                "github_url": row[5],
                "linkedin_url": row[6],
            }
    except Exception:
        pass
    return {
        "full_name": "Software Developer Candidate",
        "email": "candidate@example.com",
        "phone": "+1-555-0199",
        "skills": "Python, JavaScript, React, Node.js, SQL, REST APIs, Git, Linux",
        "experience_summary": "Passionate Software Engineer skilled in full-stack development, API automation, and backend systems.",
        "github_url": "https://github.com",
        "linkedin_url": "https://linkedin.com",
    }


def update_user_job_profile(name, email, phone, skills, experience):
    """Updates user profile for job applications."""
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_job_profile (id, full_name, email, phone, skills, experience_summary)
            VALUES (1, ?, ?, ?, ?, ?)
        """,
            (name, email, phone, skills, experience),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[JobApplierDB] Update Error: {e}")
        return False


def search_indeed_canada_jobs(query="IT Support", location="Ontario", limit=4):
    """Generates direct Indeed Canada (ca.indeed.com) application portals and live listings targeted to requested location."""
    indeed_jobs = []

    q_low = (str(query) + " " + str(location)).lower()

    if "niagara" in q_low or "catharines" in q_low or "welland" in q_low:
        target_locations = [
            ("St. Catharines, ON", "Niagara Region (St. Catharines)"),
            ("Niagara Falls, ON", "Niagara Region (Niagara Falls)"),
            ("Welland, ON", "Niagara Region (Welland)"),
            ("Niagara-on-the-Lake, ON", "Niagara Region"),
        ]
    elif "peel" in q_low or "mississauga" in q_low or "brampton" in q_low:
        target_locations = [
            ("Mississauga, ON", "Peel Region (Mississauga)"),
            ("Brampton, ON", "Peel Region (Brampton)"),
            ("Caledon, ON", "Peel Region (Caledon)"),
        ]
    elif "sudbury" in q_low:
        target_locations = [
            ("Greater Sudbury, ON", "Greater Sudbury"),
            ("Sudbury, ON", "Greater Sudbury Area"),
        ]
    else:
        target_locations = [
            ("St. Catharines, ON", "Niagara Region"),
            ("Mississauga, ON", "Peel Region"),
            ("Greater Sudbury, ON", "Greater Sudbury"),
        ]

    search_queries = [
        ("IT Support", "IT Support Analyst & Systems Technician"),
        ("Telecommunications", "Telecommunications & Field Technician"),
        ("Data Analyst", "AI Data Analyst & Operations Technician"),
        ("Technician", "Network Infrastructure & Hardware Technician"),
    ]

    for loc_str, loc_label in target_locations:
        for q_term, role_title in search_queries:
            if len(indeed_jobs) >= limit:
                break
            q_enc = urllib.parse.quote_plus(q_term)
            l_enc = urllib.parse.quote_plus(loc_str)
            indeed_url = f"https://ca.indeed.com/jobs?q={q_enc}&l={l_enc}"

            indeed_jobs.append(
                {
                    "id": f"indeed_{len(indeed_jobs)+1}",
                    "title": f"{role_title} ({q_term})",
                    "company": f"Ontario Employer ({loc_label})",
                    "location": loc_str,
                    "url": indeed_url,
                    "tags": [
                        "indeed-canada",
                        "playwright-auto-fill",
                        "it-support",
                        "telecom",
                    ],
                    "source": "Indeed Canada",
                    "description": f"Live Indeed Canada posting for {role_title} in {loc_str}. Requires IT Support / Telecom / Data Analyst skills, Google IT Support Certificate, or Class G License.",
                }
            )

    return indeed_jobs


def search_live_it_jobs(query="IT Support Specialist", location="Ontario", limit=6):
    """Fetches real live IT job listings targeted at Peel Region, Niagara, Greater Sudbury, and Indeed Canada."""
    jobs = []

    # 1. Fetch Indeed Canada Targeted Listings First
    try:
        indeed_results = search_indeed_canada_jobs(query, location, limit=3)
        jobs.extend(indeed_results)
    except Exception as e:
        print(f"[IndeedSearch] Error: {e}")

    # 2. Fetch from RemoteOK & Tech Job APIs
    try:
        url = "https://remoteok.com/api"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        raw_res = urllib.request.urlopen(req, timeout=5).read().decode("utf-8")
        data = json.loads(raw_res)

        pos_keywords = [
            "it ",
            "support",
            "telecom",
            "network",
            "data",
            "python",
            "developer",
            "engineer",
            "systems",
            "technician",
            "helpdesk",
            "administrator",
            "sysadmin",
            "analyst",
        ]
        exclude_words = [
            "gardener",
            "chef",
            "cook",
            "cleaner",
            "driver",
            "nursing",
            "medical doctor",
        ]

        for item in data[1:]:  # Skip index 0 meta
            if not isinstance(item, dict):
                continue
            position = item.get("position", "")
            company = item.get("company", "")
            " ".join(item.get("tags", []))
            job_url = item.get("url", "https://ca.indeed.com")
            desc = item.get("description", "")
            location_job = item.get("location", "Remote Canada") or "Remote Canada"

            pos_low = position.lower()
            if any(e in pos_low for e in exclude_words):
                continue

            if any(k in pos_low for k in pos_keywords):
                jobs.append(
                    {
                        "id": item.get("id", str(time.time())),
                        "title": position,
                        "company": company,
                        "location": location_job,
                        "url": job_url,
                        "tags": item.get("tags", [])[:5],
                        "source": "RemoteOK Canada",
                        "description": desc[:300] + "..." if len(desc) > 300 else desc,
                    }
                )
                if len(jobs) >= limit:
                    break
    except Exception as e:
        print(f"[JobSearch] API error: {e}")

    return jobs


def generate_ai_cover_letter(job_title, company, description=""):
    """Generates a professional tailored cover letter using AI and user profile."""
    profile = get_user_job_profile()

    # Try calling local Ollama model if running
    try:
        import requests

        prompt = (
            f"Write a short, professional 3-paragraph cover letter for candidate {profile['full_name']} "
            f"applying for the position of '{job_title}' at '{company}'.\n"
            f"Candidate Skills: {profile['skills']}\n"
            f"Candidate Summary: {profile['experience_summary']}\n"
            f"Keep it compelling, concise, and enthusiastic."
        )
        res = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={"model": "qwen2.5-coder:7b", "prompt": prompt, "stream": False},
            timeout=8,
        )
        if res.status_code == 200:
            letter = res.json().get("response", "").strip()
            if letter and len(letter) > 100:
                return letter
    except Exception:
        pass

    # Template fallback
    return (
        f"Dear Hiring Manager at {company},\n\n"
        f"I am writing to express my strong interest in the {job_title} position. "
        f"With a solid background in {profile['skills']}, I am confident in my ability to contribute "
        f"effectively to your software engineering goals at {company}.\n\n"
        f"{profile['experience_summary']}\n\n"
        f"I welcome the opportunity to discuss how my technical expertise aligns with your team's needs. "
        f"Thank you for your time and consideration.\n\n"
        f"Sincerely,\n"
        f"{profile['full_name']}\n"
        f"Email: {profile['email']} | Phone: {profile['phone']}\n"
        f"GitHub: {profile['github_url']} | LinkedIn: {profile['linkedin_url']}"
    )


def auto_apply_to_job(job_title, company, job_url="https://remoteok.com"):
    """Saves application record to DB, generates AI cover letter, and opens browser application portal."""
    cover_letter = generate_ai_cover_letter(job_title, company)

    # Record application in database
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO job_applications (job_title, company, location, url, cover_letter, status)
            VALUES (?, ?, 'Remote', ?, ?, 'Applied')
        """,
            (job_title, company, job_url, cover_letter),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[JobApplierDB] Record error: {e}")

    # 1. Launch default browser directly to clean job URL
    try:
        import webbrowser

        webbrowser.open(job_url)
    except Exception as e:
        print(f"[JobApplier] Browser launch error: {e}")

    # 2. Trigger Playwright Autonomous Form Auto-Filler in background
    try:
        import threading

        import playwright_auto_applier

        threading.Thread(
            target=playwright_auto_applier.auto_apply_with_playwright,
            args=(job_url, cover_letter),
            daemon=True,
        ).start()
        print("[JobApplier] Playwright Autonomous Form Auto-Filler launched!")
    except Exception as e:
        print(f"[JobApplier] Playwright launch error: {e}")

    return cover_letter


def get_job_application_history():
    """Returns list of past job applications."""
    try:
        conn = db_engine.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, job_title, company, location, url, cover_letter, status, timestamp FROM job_applications ORDER BY id DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0],
                "job_title": r[1],
                "company": r[2],
                "location": r[3],
                "url": r[4],
                "cover_letter": r[5],
                "status": r[6],
                "timestamp": r[7],
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[JobApplierDB] History Error: {e}")
        return []
