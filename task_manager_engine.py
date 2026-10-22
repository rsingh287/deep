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


class TaskManagerEngine:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(**DB_PARAMS)

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tasks
                     (id SERIAL PRIMARY KEY, 
                      title TEXT, 
                      category TEXT, 
                      status TEXT, 
                      created_at TIMESTAMP)""")
        conn.commit()
        conn.close()

    def add_task(self, title, category="General"):
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.datetime.now()
        c.execute(
            "INSERT INTO tasks (title, category, status, created_at) VALUES (%s, %s, %s, %s)",
            (title, category, "pending", now),
        )
        conn.commit()
        conn.close()
        return f"Task added: '{title}' [{category}]"

    def complete_task(self, task_id=None, title=None):
        conn = self._get_connection()
        c = conn.cursor()
        if task_id:
            c.execute("UPDATE tasks SET status='completed' WHERE id=%s", (task_id,))
            msg = f"Marked task {task_id} as completed."
        elif title:
            c.execute(
                "UPDATE tasks SET status='completed' WHERE title ILIKE %s AND status='pending'",
                (f"%{title}%",),
            )
            msg = f"Marked tasks matching '{title}' as completed."
        else:
            msg = "Please provide task_id or title to complete."
        conn.commit()
        conn.close()
        return msg

    def get_pending_tasks(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT id, title, category FROM tasks WHERE status='pending'")
        tasks = c.fetchall()
        conn.close()

        if not tasks:
            return "You have no pending tasks. Great job!"

        report = ["Your Pending Tasks:"]
        for t in tasks:
            report.append(f"- [{t[0]}] {t[1]} ({t[2]})")
        return "\n".join(report)

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "add_task":
            title = intent_data.get("title", "")
            category = intent_data.get("category", "General")
            return self.add_task(title, category)
        elif action == "complete_task":
            title = intent_data.get("title", None)
            task_id = intent_data.get("task_id", None)
            return self.complete_task(task_id, title)
        elif action == "get_tasks":
            return self.get_pending_tasks()
        else:
            return "Unknown task manager action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = TaskManagerEngine()
    print("Task Manager Engine Ready")
