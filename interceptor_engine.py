"""
Interceptor Engine for Antigravity Local AI PC Cockpit
Inspects, sanitizes, and intercepts AI agent actions, shell execution, and security risks.
Provides real-time audit logging into memory.db.
"""

import os
import re
from typing import Any, Dict, List, Tuple

import db_engine

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.db")

BLOCKED_PATTERNS = [
    (r"format\s+[a-zA-Z]:", "System disk format command"),
    (r"del\s+/[fFqsS]*\s+[cC]:[\\/]", "Mass root directory deletion"),
    (r"rmdir\s+/[sS]\s+/[qQ]\s+[cC]:[\\/]", "Recursive root directory purge"),
    (r"reg\s+(?:delete|add)\s+hklm", "Registry system hive modification"),
    (r"Set-ItemProperty\s+.*hklm", "PowerShell registry alteration"),
    (r"vssadmin\s+delete\s+shadows", "Shadow copy deletion (ransomware indicator)"),
    (r"net\s+user\s+.*\s+/add", "Unauthorized user account creation"),
    (r"curl\s+.*\|\s*(?:bash|sh|powershell|cmd)", "Remote script piping into shell"),
]


def _init_db():
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS security_interceptions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT,
            target TEXT,
            status TEXT,
            reason TEXT,
            severity TEXT
        )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Interceptor] DB init error: {e}")


_init_db()


def intercept_action(
    action_type: str, payload: str
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Evaluates whether an action/command is safe to proceed.
    Returns (is_allowed: bool, message: str, audit_entry: dict).
    """
    if not payload:
        return True, "Allowed", {}

    payload_clean = payload.strip().lower()

    # Check blocked patterns
    for pat, desc in BLOCKED_PATTERNS:
        if re.search(pat, payload_clean, re.IGNORECASE):
            log_entry = {
                "action_type": action_type,
                "target": payload[:120],
                "status": "BLOCKED",
                "reason": f"Security Guardrail: {desc}",
                "severity": "CRITICAL",
            }
            _record_log(log_entry)
            return False, f"🛑 **Interceptor Blocked Action:** {desc}.", log_entry

    # Allowed
    log_entry = {
        "action_type": action_type,
        "target": payload[:120],
        "status": "ALLOWED",
        "reason": "Passed security filters",
        "severity": "LOW",
    }
    _record_log(log_entry)
    return True, "Action allowed.", log_entry


def _record_log(entry: Dict[str, Any]):
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute(
            """
        INSERT INTO security_interceptions (action_type, target, status, reason, severity)
        VALUES (?, ?, ?, ?, ?)
        """,
            (
                entry.get("action_type"),
                entry.get("target"),
                entry.get("status"),
                entry.get("reason"),
                entry.get("severity"),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Interceptor] Log record error: {e}")


def get_recent_interceptions(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves the latest audit events from the database."""
    logs = []
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute(
            """
        SELECT id, timestamp, action_type, target, status, reason, severity
        FROM security_interceptions
        ORDER BY id DESC LIMIT ?
        """,
            (limit,),
        )
        for row in c.fetchall():
            logs.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "action_type": row[2],
                    "target": row[3],
                    "status": row[4],
                    "reason": row[5],
                    "severity": row[6],
                }
            )
        conn.close()
    except Exception as e:
        print(f"[Interceptor] Fetch logs error: {e}")
    return logs
