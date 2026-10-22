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


class HealthFitnessTracker:
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(**DB_PARAMS)

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS fitness_logs
                     (id SERIAL PRIMARY KEY, 
                      log_type TEXT, 
                      value REAL, 
                      unit TEXT, 
                      date TIMESTAMP)""")
        conn.commit()
        conn.close()

    def log_metric(self, log_type, value, unit):
        conn = self._get_connection()
        c = conn.cursor()
        now = datetime.datetime.now()
        c.execute(
            "INSERT INTO fitness_logs (log_type, value, unit, date) VALUES (%s, %s, %s, %s)",
            (log_type, value, unit, now),
        )
        conn.commit()
        conn.close()
        return f"Logged {log_type}: {value} {unit}"

    def get_daily_summary(self):
        today_start = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        conn = self._get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT log_type, SUM(value), unit FROM fitness_logs WHERE date >= %s GROUP BY log_type, unit",
            (today_start,),
        )
        data = c.fetchall()
        conn.close()

        if not data:
            return "No health or fitness data logged today."

        report = ["Today's Health & Fitness Summary:"]
        for row in data:
            report.append(f"- {row[0].capitalize()}: {row[1]:.2f} {row[2]}")
        return "\n".join(report)

    def process_intent(self, intent_data):
        action = intent_data.get("action", "")
        if action == "log_metric":
            log_type = intent_data.get("log_type", "calories")
            value = float(intent_data.get("value", 0))
            unit = intent_data.get("unit", "")
            return self.log_metric(log_type, value, unit)
        elif action == "get_summary":
            return self.get_daily_summary()
        else:
            return "Unknown fitness action."


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    engine = HealthFitnessTracker()
    print("Health & Fitness Tracker Ready")
