import db_engine

def fix_sequences():
    conn = db_engine.get_db_connection()
    cur = conn.cursor()
    tables = [
        'security_interceptions',
        'chat_messages',
        'job_applications',
        'user_job_profile',
        'learned_skills',
        'quant_forecast_history',
        'live_paper_orders',
        'live_real_money_orders',
        'facts',
        'active_skill_session'
    ]
    for t in tables:
        seq = f"{t}_id_seq"
        cur.execute(f"CREATE SEQUENCE IF NOT EXISTS {seq}")
        cur.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {t}")
        row = cur.fetchone()
        max_id = row[0] if isinstance(row, (list, tuple)) else row['coalesce']
        cur.execute(f"SELECT setval('{seq}', {max_id}, false)")
        cur.execute(f"ALTER TABLE {t} ALTER COLUMN id SET DEFAULT nextval('{seq}')")
        print(f"Fixed sequence for {t} (next id: {max_id})")
    conn.commit()
    conn.close()
    print("All sequences configured successfully!")

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    fix_sequences()
