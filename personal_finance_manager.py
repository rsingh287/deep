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


class PersonalFinanceManager:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(**DB_PARAMS)

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS expenses
                     (id SERIAL PRIMARY KEY, 
                      amount REAL, 
                      category TEXT, 
                      description TEXT, 
                      date TIMESTAMP)""")
        conn.commit()
        conn.close()

    def add_expense(self, amount, category, description=""):
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.datetime.now()
        c.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (%s, %s, %s, %s)",
            (amount, category, description, now),
        )
        conn.commit()
        conn.close()
        return f"Logged expense: ${amount:.2f} for {category} ({description})"

    def get_summary(self, days=7):
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE date >= %s GROUP BY category",
            (cutoff,),
        )
        data = c.fetchall()
        conn.close()

        if not data:
            return f"No expenses logged in the last {days} days."

        total = sum([row[1] for row in data])
        report = [f"Expense Summary (Last {days} Days):"]
        for row in data:
            report.append(f"- {row[0]}: ${row[1]:.2f}")
        report.append(f"Total: ${total:.2f}")

        return "\n".join(report)

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "add_expense":
            amount = float(intent_data.get("amount", 0.0))
            category = intent_data.get("category", "General")
            desc = intent_data.get("description", "")
            return self.add_expense(amount, category, desc)
        elif action == "get_summary":
            days = int(intent_data.get("days", 7))
            return self.get_summary(days)
        else:
            return "Unknown finance action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = PersonalFinanceManager()
    print("Personal Finance Manager Ready")
