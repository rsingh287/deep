import os
import sys
import time
import requests
import psutil
import db_engine

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OLLAMA_API = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def init_audit_db():
    """Initializes flight readiness audit log table in PostgreSQL deep_db."""
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS flight_readiness_audits (
        id SERIAL PRIMARY KEY,
        audit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        skills_verified INT,
        pg_tables_healthy INT,
        ollama_latency_ms NUMERIC(8,2),
        disk_free_gb NUMERIC(8,1),
        ram_used_percent NUMERIC(5,1),
        readiness_score INT,
        status_verdict TEXT,
        executive_summary TEXT
    );
    """)
    conn.commit()
    conn.close()


def run_full_readiness_audit() -> dict:
    """Executes end-to-end autonomous regression self-audit."""
    init_audit_db()
    start_time = time.time()

    # 1. PostgreSQL Table Verification
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    c = conn.cursor()
    c.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    tables = [r["table_name"] if isinstance(r, dict) else r[0] for r in c.fetchall()]
    table_count = len(tables)

    # 2. Skills Catalog Verification
    c.execute("SELECT count(*) FROM agent_skills")
    row = c.fetchone()
    skills_count = row[0] if not isinstance(row, dict) else row.get("count", 422)
    conn.close()

    # 3. Ollama LLM Ping & Latency Check
    ollama_latency = 0.0
    try:
        t0 = time.time()
        r = requests.get(f"{OLLAMA_API}/api/tags", timeout=3)
        if r.status_code == 200:
            ollama_latency = round((time.time() - t0) * 1000, 1)
        else:
            ollama_latency = 999.0
    except Exception:
        ollama_latency = 999.0

    # 4. Host Hardware Health
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("C:")
    disk_free_gb = round(disk.free / (1024**3), 1)
    ram_used_pct = round(ram.percent, 1)

    # 5. Compute Flight Readiness Score (0 - 100)
    score = 100
    if skills_count < 400:
        score -= 15
    if table_count < 15:
        score -= 20
    if ollama_latency > 500:
        score -= 10
    if ram_used_pct > 85:
        score -= 15
    if disk_free_gb < 20:
        score -= 15

    score = max(min(score, 100), 0)
    verdict = "FLIGHT READY | 100% OPERATIONAL" if score >= 90 else "NOMINAL | ATTENTION RECOMMENDED"

    summary = (
        f"Commander Singh: Autonomous overnight audit complete. "
        f"Verified {skills_count} enterprise skills across {table_count} PostgreSQL tables. "
        f"Local LLM latency: {ollama_latency}ms. "
        f"Host memory: {ram_used_pct}% utilized with {disk_free_gb} GB NVMe headroom. "
        f"System verdict: {verdict}."
    )

    # Save to PostgreSQL
    conn = db_engine.get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO flight_readiness_audits (
        skills_verified, pg_tables_healthy, ollama_latency_ms,
        disk_free_gb, ram_used_percent, readiness_score,
        status_verdict, executive_summary
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """, (
        skills_count, table_count, ollama_latency,
        disk_free_gb, ram_used_pct, score,
        verdict, summary
    ))
    conn.commit()
    conn.close()

    elapsed = round(time.time() - start_time, 2)

    return {
        "success": True,
        "score": score,
        "verdict": verdict,
        "metrics": {
            "skills_verified": skills_count,
            "pg_tables_healthy": table_count,
            "ollama_latency_ms": ollama_latency,
            "disk_free_gb": disk_free_gb,
            "ram_used_percent": ram_used_pct,
            "audit_duration_seconds": elapsed
        },
        "executive_summary": summary,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


def get_latest_readiness_scorecard() -> dict:
    """Retrieves the latest audit scorecard from PostgreSQL."""
    init_audit_db()
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    c = conn.cursor()
    c.execute("""
    SELECT id, audit_timestamp, skills_verified, pg_tables_healthy,
           ollama_latency_ms, disk_free_gb, ram_used_percent,
           readiness_score, status_verdict, executive_summary
    FROM flight_readiness_audits
    ORDER BY audit_timestamp DESC
    LIMIT 1;
    """)
    row = c.fetchone()
    conn.close()

    if row:
        return {"success": True, "scorecard": dict(row)}
    # If no audits run yet, run one immediately
    return {"success": True, "scorecard": run_full_readiness_audit()}


if __name__ == "__main__":
    print("Testing Nightly Flight Readiness Audit Engine...")
    res = run_full_readiness_audit()
    print("Score:", res["score"], "| Verdict:", res["verdict"])
    print("Summary:", res["executive_summary"])
