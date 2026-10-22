import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()


class RowDict(dict):
    """Hybrid dictionary that supports integer indexing (row[0]) and key indexing (row['col']) like sqlite3.Row."""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class PostgresCursorAdapter:
    def __init__(self, pg_cursor, is_dict_cursor=False):
        self.pg_cursor = pg_cursor
        self.is_dict_cursor = is_dict_cursor
        self._lastrowid = None

    def execute(self, query, params=None):
        new_query = query
        if params:
            new_query = new_query.replace("?", "%s")

        is_insert = query.strip().upper().startswith("INSERT")
        if is_insert and "RETURNING" not in query.upper():
            try:
                self.pg_cursor.execute("SAVEPOINT sp_returning_id")
                try_query = new_query.rstrip("; ") + " RETURNING id"
                if params:
                    self.pg_cursor.execute(try_query, params)
                else:
                    self.pg_cursor.execute(try_query)
                self.pg_cursor.execute("RELEASE SAVEPOINT sp_returning_id")
                try:
                    row = self.pg_cursor.fetchone()
                    if row:
                        self._lastrowid = dict(row).get("id", list(dict(row).values())[0]) if self.is_dict_cursor else row[0]
                except Exception:
                    pass
                return
            except Exception:
                self.pg_cursor.execute("ROLLBACK TO SAVEPOINT sp_returning_id")

        if params:
            self.pg_cursor.execute(new_query, params)
        else:
            self.pg_cursor.execute(new_query)

    def fetchall(self):
        rows = self.pg_cursor.fetchall()
        if self.is_dict_cursor and rows:
            return [RowDict(r) for r in rows]
        return rows

    def fetchone(self):
        row = self.pg_cursor.fetchone()
        if self.is_dict_cursor and row:
            return RowDict(row)
        return row

    def fetchmany(self, size):
        rows = self.pg_cursor.fetchmany(size)
        if self.is_dict_cursor and rows:
            return [RowDict(r) for r in rows]
        return rows

    def close(self):
        self.pg_cursor.close()

    @property
    def lastrowid(self):
        return self._lastrowid


class PostgresConnectionAdapter:
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn
        self._row_factory = None

    @property
    def row_factory(self):
        return self._row_factory

    @row_factory.setter
    def row_factory(self, factory):
        self._row_factory = factory

    def cursor(self):
        is_dict_cursor = self._row_factory is not None
        if is_dict_cursor:
            pg_cursor = self.pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:
            pg_cursor = self.pg_conn.cursor()
        return PostgresCursorAdapter(pg_cursor, is_dict_cursor)

    def commit(self):
        self.pg_conn.commit()

    def rollback(self):
        self.pg_conn.rollback()

    def close(self):
        self.pg_conn.close()


DEFAULT_PG_URL = f"postgresql://postgres:{os.getenv('DB_PASSWORD', '')}@localhost:5432/deep_db"

def get_db_connection():
    db_url = os.getenv("DATABASE_URL") or DEFAULT_PG_URL
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
        return PostgresConnectionAdapter(conn)
    except Exception as e:
        print(f"[PostgresEngine] Primary connection error: {e}. Retrying local default...")
        try:
            conn = psycopg2.connect(DEFAULT_PG_URL, connect_timeout=5)
            return PostgresConnectionAdapter(conn)
        except Exception as e2:
            print(f"[PostgresEngine] Critical: PostgreSQL deep_db connection failed: {e2}")
            raise e2


def execute_query(query, params=None):
    """Executes a query and returns fetched rows or affected count."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    try:
        rows = cur.fetchall()
    except Exception:
        try:
            rows = cur.fetchone()
        except Exception:
            rows = True
    conn.commit()
    conn.close()
    return rows

