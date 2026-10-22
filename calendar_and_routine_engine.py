import os
import datetime

import psycopg2

DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    r"password": os.getenv("DB_PASSWORD", ""),
    "host": "localhost",
    "port": "5432",
}


class CalendarRoutineEngine:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(**DB_PARAMS)

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS reminders
                     (id SERIAL PRIMARY KEY, 
                      title TEXT, 
                      due_time TIMESTAMP, 
                      status TEXT)""")
        conn.commit()
        conn.close()

    def add_reminder(self, title, due_time_str):
        # expects format like "YYYY-MM-DD HH:MM:SS"
        try:
            due_time = datetime.datetime.strptime(due_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Invalid time format. Please use 'YYYY-MM-DD HH:MM:SS'."

        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (title, due_time, status) VALUES (%s, %s, %s)",
            (title, due_time, "pending"),
        )
        conn.commit()
        conn.close()
        return f"Reminder added: '{title}' at {due_time_str}"

    def check_due_reminders(self):
        now = datetime.datetime.now()
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT id, title, due_time FROM reminders WHERE status='pending' AND due_time <= %s",
            (now,),
        )
        due = c.fetchall()

        results = []
        for r in due:
            results.append(f"REMINDER: {r[1]} (was due at {r[2]})")
            c.execute("UPDATE reminders SET status='completed' WHERE id=%s", (r[0],))

        conn.commit()
        conn.close()

        if not results:
            return "No due reminders at this time."
        return "\n".join(results)

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "add_reminder":
            title = intent_data.get("title", "")
            time_str = intent_data.get("due_time", "")
            return self.add_reminder(title, time_str)
        elif action == "check_reminders":
            return self.check_due_reminders()
        else:
            return "Unknown calendar action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = CalendarRoutineEngine()
    print("Calendar & Routine Engine Ready")
