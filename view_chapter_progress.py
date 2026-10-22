import sys

import db_engine

sys.stdout.reconfigure(encoding="utf-8")

conn = db_engine.get_db_connection()
cursor = conn.cursor()

print("=" * 60)
print("📚 CHAPTER PROGRESS TABLE (`chapter_progress`):")
print("=" * 60)
cursor.execute("SELECT * FROM chapter_progress")
rows = cursor.fetchall()
if not rows:
    print("No rows found in chapter_progress.")
for r in rows:
    print(r)

print("\n" + "=" * 60)
print("🎓 LEARNED SKILLS TABLE (`learned_skills`):")
print("=" * 60)
cursor.execute("SELECT * FROM learned_skills")
l_rows = cursor.fetchall()
if not l_rows:
    print("No rows found in learned_skills.")
for r in l_rows:
    print(r)

print("\n" + "=" * 60)
print("🧠 INTERACTIVE ACADEMY & TUTOR FILES:")
print("=" * 60)
import os

for fname in [
    "interactive_learning_academy.py",
    "autonomous_online_learner_tutor.py",
    "expert_tutor_engine.py",
]:
    if os.path.exists(fname):
        print(f"✅ {fname} exists ({os.path.getsize(fname)} bytes)")
