import os
import sqlite3

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def migrate():
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "memory.db")
    pg_url = os.getenv("DATABASE_URL")

    if not os.path.exists(sqlite_db_path):
        print(f"SQLite DB not found at {sqlite_db_path}")
        return

    if not pg_url or not pg_url.startswith("postgres"):
        print("DATABASE_URL not set or invalid in .env")
        return

    try:
        pg_conn = psycopg2.connect(pg_url)
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        print(
            "Please ensure PostgreSQL is running, the credentials in .env are correct, and the database 'deep_db' exists."
        )
        return

    pg_cursor = pg_conn.cursor()
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    # 1. Get all tables from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = sqlite_cursor.fetchall()

    for (table_name,) in tables:
        if table_name == "sqlite_sequence":
            continue

        print(f"Migrating table: {table_name}")

        # 2. Get table schema from SQLite
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = sqlite_cursor.fetchall()

        # Construct CREATE TABLE for PostgreSQL
        col_defs = []
        for col in columns:
            col_id, name, type_, notnull, default, pk = col
            pg_type = type_.upper()

            # Map SQLite types to PostgreSQL types
            if "INT" in pg_type:
                pg_type = "INTEGER"
            elif "CHAR" in pg_type or "CLOB" in pg_type or "TEXT" in pg_type:
                pg_type = "TEXT"
            elif "REAL" in pg_type or "FLOA" in pg_type or "DOUB" in pg_type:
                pg_type = "REAL"
            elif "BLOB" in pg_type:
                pg_type = "BYTEA"
            else:
                pg_type = "TEXT"  # fallback

            col_def = f"{name} {pg_type}"
            if pk:
                col_def += " PRIMARY KEY"
            if notnull:
                col_def += " NOT NULL"

            col_defs.append(col_def)

        create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(col_defs)})"

        try:
            pg_cursor.execute(create_stmt)
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
            pg_conn.rollback()
            continue

        # 3. Transfer data
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if rows:
            placeholders = ", ".join(["%s"] * len(columns))
            insert_stmt = f"INSERT INTO {table_name} VALUES ({placeholders})"
            try:
                pg_cursor.executemany(insert_stmt, rows)
            except Exception as e:
                print(f"Error inserting data into {table_name}: {e}")
                pg_conn.rollback()
                continue

        pg_conn.commit()
        print(f"Successfully migrated {len(rows)} rows for {table_name}.")

    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    migrate()
