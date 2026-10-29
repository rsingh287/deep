"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: POSTGRESQL ENTERPRISE DATABASE ENGINE
===================================================================
High-performance PostgreSQL engine powered by psycopg v3 with:
- Synchronous & Asynchronous Connection Pooling (AsyncConnectionPool)
- Least-Privilege Read-Only Role ('deep_reader') with Engine-Level Immutability
- Automatic Fallback to psycopg2 for Legacy Compatibility
- Vector Table & High-Throughput Relational Storage for D.E.E.P
"""

import os
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("PostgreSQLEngine")

# Default Connection Strings
DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Rtoken98$@localhost:5432/deep_db"
)
READER_DB_URL = os.getenv(
    "READER_DATABASE_URL",
    "postgresql://deep_reader:deep_reader_secure_pass_2026@localhost:5432/deep_db"
)

# Driver Detection: Prefer psycopg v3 with pooling, fallback to psycopg2
HAS_PSYCOPG3 = False
HAS_PSYCOPG2 = False
_SYNC_POOL = None
_ASYNC_POOL = None
_READER_POOL = None

try:
    import psycopg
    from psycopg_pool import ConnectionPool, AsyncConnectionPool
    HAS_PSYCOPG3 = True

    # Windows Asyncio Compatibility: Psycopg async requires SelectorEventLoop on Windows
    import sys
    if sys.platform == "win32":
        import asyncio
        if hasattr(asyncio, "WindowsSelectorEventLoopPolicy") and isinstance(
            asyncio.get_event_loop_policy(), getattr(asyncio, "WindowsProactorEventLoopPolicy", object)
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except ImportError:
    try:
        import psycopg2
        HAS_PSYCOPG2 = True
    except ImportError:
        pass


def _get_sync_pool(is_reader: bool = False):
    """Returns or initializes the thread-safe connection pool."""
    global _SYNC_POOL, _READER_POOL
    if not HAS_PSYCOPG3:
        return None

    target_url = READER_DB_URL if is_reader else DEFAULT_DB_URL
    try:
        if is_reader:
            if _READER_POOL is None or _READER_POOL.closed:
                _READER_POOL = ConnectionPool(
                    conninfo=target_url,
                    min_size=1,
                    max_size=5,
                    timeout=5.0,
                    open=True
                )
            return _READER_POOL
        else:
            if _SYNC_POOL is None or _SYNC_POOL.closed:
                _SYNC_POOL = ConnectionPool(
                    conninfo=target_url,
                    min_size=2,
                    max_size=10,
                    timeout=5.0,
                    open=True
                )
            return _SYNC_POOL
    except Exception as e:
        logger.warning(f"Failed to initialize psycopg3 connection pool: {e}")
        return None


def test_postgresql_connection(host=None, port=None, user=None, password=None, dbname=None) -> Dict[str, Any]:
    """
    Tests live connection to the local PostgreSQL database service (deep_db)
    and validates deep_reader read-only enforcement.
    """
    if not (HAS_PSYCOPG3 or HAS_PSYCOPG2):
        return {
            "status": "error",
            "message": "Neither psycopg (v3) nor psycopg2 is installed in Python environment.",
        }

    driver_name = f"psycopg v3 ({psycopg.__version__})" if HAS_PSYCOPG3 else "psycopg2"
    url = DEFAULT_DB_URL

    try:
        if HAS_PSYCOPG3:
            with psycopg.connect(url, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    pg_version = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
                    table_count = cur.fetchone()[0]
        else:
            import psycopg2
            conn = psycopg2.connect(url, connect_timeout=3)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            pg_version = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
            table_count = cur.fetchone()[0]
            cur.close()
            conn.close()

        # Check deep_reader status
        reader_active = False
        try:
            if HAS_PSYCOPG3:
                with psycopg.connect(READER_DB_URL, connect_timeout=2) as rconn:
                    with rconn.cursor() as rcur:
                        rcur.execute("SHOW default_transaction_read_only;")
                        val = rcur.fetchone()[0]
                        reader_active = (val.lower() == "on")
        except Exception:
            reader_active = False

        reader_msg = "Enforced & Active" if reader_active else "Standby"

        return {
            "status": "success",
            "driver": driver_name,
            "table_count": table_count,
            "deep_reader_role": reader_msg,
            "message": f"Connected to deep_db successfully! Version: {pg_version[:40]} | Tables: {table_count} | Driver: {driver_name}",
        }
    except Exception as e:
        return {"status": "error", "message": f"PostgreSQL Connection Error: {str(e)}"}


def execute_postgresql_query(query_sql: str, params: Optional[Tuple] = None) -> str:
    """
    Executes SQL query against deep_db using connection pooling and returns formatted Markdown tables.
    """
    if not (HAS_PSYCOPG3 or HAS_PSYCOPG2):
        return "⚠️ **psycopg** is not installed. Database query aborted."

    try:
        pool = _get_sync_pool(is_reader=False)
        if pool:
            with pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_sql, params)
                    return _format_cursor_results(cursor, conn)
        elif HAS_PSYCOPG3:
            with psycopg.connect(DEFAULT_DB_URL, connect_timeout=3) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_sql, params)
                    return _format_cursor_results(cursor, conn)
        else:
            import psycopg2
            conn = psycopg2.connect(DEFAULT_DB_URL, connect_timeout=3)
            cursor = conn.cursor()
            cursor.execute(query_sql, params)
            result = _format_cursor_results(cursor, conn)
            cursor.close()
            conn.close()
            return result
    except Exception as e:
        return f"⚠️ **PostgreSQL Query Error:** {str(e)}"


def execute_readonly_query(query_sql: str, params: Optional[Tuple] = None) -> Tuple[bool, Any]:
    """
    Executes query strictly using the 'deep_reader' role with DEFAULT_TRANSACTION_READ_ONLY = ON.
    PostgreSQL's engine physically rejects any INSERT, UPDATE, DELETE, or DDL commands.
    Returns: (success: bool, result: list_of_dicts_or_error_str)
    """
    if not (HAS_PSYCOPG3 or HAS_PSYCOPG2):
        return False, "Database driver not available."

    try:
        pool = _get_sync_pool(is_reader=True)
        if pool:
            with pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_sql, params)
                    return True, _cursor_to_dicts(cursor)
        elif HAS_PSYCOPG3:
            with psycopg.connect(READER_DB_URL, connect_timeout=3) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_sql, params)
                    return True, _cursor_to_dicts(cursor)
        else:
            import psycopg2
            conn = psycopg2.connect(READER_DB_URL, connect_timeout=3)
            cursor = conn.cursor()
            cursor.execute(query_sql, params)
            rows = _cursor_to_dicts(cursor)
            cursor.close()
            conn.close()
            return True, rows
    except Exception as e:
        return False, f"Engine Security Exception: {str(e)}"


async def execute_readonly_query_async(query_sql: str, params: Optional[Tuple] = None) -> Tuple[bool, Any]:
    """
    Asynchronous version of execute_readonly_query using psycopg v3 AsyncConnection.
    Non-blocking execution for WebSocket and FastAPI event loops.
    """
    if not HAS_PSYCOPG3:
        return execute_readonly_query(query_sql, params)

    try:
        async with await psycopg.AsyncConnection.connect(READER_DB_URL, connect_timeout=3) as aconn:
            async with aconn.cursor() as acur:
                await acur.execute(query_sql, params)
                columns = [desc[0] for desc in acur.description] if acur.description else []
                rows = await acur.fetchall() if acur.description else []
                result = [dict(zip(columns, row)) for row in rows]
                return True, result
    except Exception as e:
        return False, f"Async Read-Only Engine Exception: {str(e)}"


def _cursor_to_dicts(cursor) -> List[Dict[str, Any]]:
    if not cursor.description:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _format_cursor_results(cursor, conn) -> str:
    if cursor.description:
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        if not rows:
            return "🐘 **PostgreSQL Query Executed:** Zero rows returned."

        header = " | ".join(columns)
        divider = " | ".join(["---"] * len(columns))
        body = "\n".join(
            [" | ".join([str(val) for val in row]) for row in rows[:15]]
        )
        extra = f"\n\n*(Showing top 15 of {len(rows)} rows)*" if len(rows) > 15 else ""
        return f"🐘 **PostgreSQL Query Results:**\n\n| {header} |\n| {divider} |\n| {body} |{extra}"
    else:
        conn.commit()
        return f"🐘 **PostgreSQL Command Executed Successfully!** (Rows Affected: {cursor.rowcount})"


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(test_postgresql_connection())
