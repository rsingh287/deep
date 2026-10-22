import datetime
import sys

import db_engine
import interactive_learning_academy

sys.stdout.reconfigure(encoding="utf-8")

conn = db_engine.get_db_connection()
cursor = conn.cursor()

print("=" * 60)
print("📚 1. INTERACTIVE ACADEMY BUILT-IN COURSES:")
print("=" * 60)
for course_key, chaps in interactive_learning_academy.COURSE_CHAPTERS.items():
    print(f"• Course: {course_key.upper()} ({len(chaps)} Chapters Available)")
    for ch in chaps:
        print(f"   - Chapter {ch['chapter']}: {ch['title']}")

print("\n" + "=" * 60)
print("🧠 2. AUTONOMOUSLY SYNTHESIZED MASTER COURSES (`learned_skills`):")
print("=" * 60)
cursor.execute("SELECT id, topic, timestamp FROM learned_skills")
rows = cursor.fetchall()
for r in rows:
    dt_str = datetime.datetime.fromtimestamp(r[2]).strftime("%Y-%m-%d %H:%M:%S")
    print(f"• Course ID {r[0]}: {r[1].title()} (Synthesized on {dt_str})")

print("\n" + "=" * 60)
print("📊 3. ACTIVE CHAPTER PROGRESS (`chapter_progress`):")
print("=" * 60)
cursor.execute("SELECT topic, current_chapter, status, weak_area FROM chapter_progress")
cp_rows = cursor.fetchall()
for cp in cp_rows:
    print(
        f"• Topic: {cp[0].upper()} | Current Chapter: {cp[1]} | Status: {cp[2]} | Notes: {cp[3]}"
    )
