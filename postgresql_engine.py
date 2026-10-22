import os
"""
===================================================================
ANTIGRAVITY AI WORKSTATION: POSTGRESQL ENTERPRISE DATABASE ENGINE
===================================================================
Connects to local/remote PostgreSQL databases, executes enterprise SQL,
manages schemas, and feeds live relational data to Power BI & Python analytics.
"""

try:
    import psycopg2

    PG_INSTALLED = True
except ImportError:
    PG_INSTALLED = False

DEFAULT_PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    r"password": os.getenv("DB_PASSWORD", ""),
    "dbname": "postgres",
}


def test_postgresql_connection(
    host="localhost", port=5432, user="postgres", password=os.getenv("DB_PASSWORD", ""), dbname="postgres"
):
    """Tests connection to local PostgreSQL service."""
    if not PG_INSTALLED:
        return {
            "status": "error",
            "message": "psycopg2 library not installed in Python environment.",
        }

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            connect_timeout=3,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "message": f"Connected to PostgreSQL successfully! Version: {pg_version[:40]}",
        }
    except Exception as e:
        return {"status": "error", "message": f"PostgreSQL Connection Error: {str(e)}"}


def execute_postgresql_query(query_sql: str):
    """Executes SQL query against PostgreSQL and returns formatted Markdown tables."""
    if not PG_INSTALLED:
        return f"⚠️ **psycopg2** is not installed. Using SQLite fallback memory.db!"

    try:
        conn = psycopg2.connect(**DEFAULT_PG_CONFIG, connect_timeout=3)
        cursor = conn.cursor()
        cursor.execute(query_sql)

        if cursor.description:  # Query returns rows (SELECT)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            header = " | ".join(columns)
            divider = " | ".join(["---"] * len(columns))
            body = "\n".join(
                [" | ".join([str(val) for val in row]) for row in rows[:10]]
            )
            return f"🐘 **PostgreSQL Query Results:**\n\n| {header} |\n| {divider} |\n| {body} |"
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return f"🐘 **PostgreSQL Command Executed Successfully!** (Rows Affected: {cursor.rowcount})"
    except Exception as e:
        return f"⚠️ **PostgreSQL Query Error:** {str(e)}"


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print(test_postgresql_connection())
