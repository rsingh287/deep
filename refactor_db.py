import glob
import os
import re


def refactor_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if no sqlite3.connect is found
    if "sqlite3.connect" not in content:
        return

    print(f"Refactoring {filepath}...")

    # 1. Add import db_engine if it's not there
    if "import db_engine" not in content:
        # Find a good place to put it: after import sqlite3 or at the top of imports
        if "import sqlite3" in content:
            content = content.replace(
                "import sqlite3", "import sqlite3\nimport db_engine"
            )
        else:
            # Just prepend
            content = "import db_engine\n" + content

    # 2. Replace sqlite3.connect(...) with db_engine.get_db_connection()
    # We use regex to match sqlite3.connect(anything)
    # Be careful with multi-line connects, but usually it's one line.
    content = re.sub(
        r"sqlite3\.connect\([^)]+\)", "db_engine.get_db_connection()", content
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    target_dir = os.path.dirname(__file__)
    py_files = glob.glob(os.path.join(target_dir, "*.py"))

    for pf in py_files:
        # Skip this file and db_engine.py
        if os.path.basename(pf) in [
            "refactor_db.py",
            "db_engine.py",
            "setup_pg.py",
            "setup_pg_brute.py",
        ]:
            continue
        refactor_file(pf)

    print("Refactoring complete.")
