import db_engine

conn = db_engine.get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print("Tables in memory.db:", tables)

for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    print(f"- {t}: {cnt} records")
    if cnt > 0:
        cursor.execute(f"SELECT * FROM {t} LIMIT 3")
        rows = cursor.fetchall()
        for r in rows:
            print("   Row:", str(r)[:150])
