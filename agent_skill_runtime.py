import os
import re
import sqlite3

import db_engine

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")
SKILLS_ROOT = r"C:\Users\User\.gemini\config\skills"
PLUGINS_ROOT = r"C:\Users\User\.gemini\config\plugins"

_SKILL_FILE_CACHE = None


def init_active_skill_table():
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS active_skill_session (
                id INTEGER PRIMARY KEY,
                skill_id TEXT,
                name TEXT,
                activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print("[AgentSkillRuntime] DB init error:", e)


init_active_skill_table()


def build_skill_file_index():
    global _SKILL_FILE_CACHE
    if _SKILL_FILE_CACHE is not None:
        return _SKILL_FILE_CACHE

    index = {}
    roots = [SKILLS_ROOT, PLUGINS_ROOT]
    for r in roots:
        if not os.path.exists(r):
            continue
        for root, dirs, files in os.walk(r):
            for f in files:
                if f.endswith(".md"):
                    full_path = os.path.join(root, f)
                    pdir = os.path.basename(root).lower().replace("-", "_")
                    fbase = os.path.splitext(f)[0].lower().replace("-", "_")

                    # Direct mappings
                    index[pdir] = full_path
                    index[fbase] = full_path

                    # Also map with hyphens
                    index[pdir.replace("_", "-")] = full_path
                    index[fbase.replace("_", "-")] = full_path

                    if "a11y_agent" in fbase or "flutter_a11y" in pdir:
                        index["flutter_a11y_agent"] = full_path
                        index["flutter-a11y-agent"] = full_path

    _SKILL_FILE_CACHE = index
    return index


def get_skill_file_path(skill_id):
    index = build_skill_file_index()
    clean_id = skill_id.lower().strip()

    # 1. Exact match
    if clean_id in index:
        return index[clean_id]

    clean_underscore = clean_id.replace("-", "_")
    if clean_underscore in index:
        return index[clean_underscore]

    clean_hyphen = clean_id.replace("_", "-")
    if clean_hyphen in index:
        return index[clean_hyphen]

    # Check partial
    for k, path in index.items():
        if clean_underscore in k or k in clean_underscore:
            return path

    return None


def get_skill_content(skill_id):
    file_path = get_skill_file_path(skill_id)
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content, file_path
        except Exception as e:
            print(f"[AgentSkillRuntime] Read error for {file_path}: {e}")
    return None, None


def set_active_skill(skill_id, name):
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM active_skill_session")
        c.execute(
            "INSERT INTO active_skill_session (id, skill_id, name) VALUES (1, ?, ?)",
            (skill_id, name),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[AgentSkillRuntime] set_active_skill error:", e)
        return False


def get_active_skill():
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT skill_id, name FROM active_skill_session WHERE id = 1")
        row = c.fetchone()
        conn.close()
        if row:
            return {"skill_id": row[0], "name": row[1]}
    except Exception as e:
        pass
    return None


def clear_active_skill():
    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM active_skill_session")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def match_relevant_skills(user_prompt, limit=2):
    """Matches user prompt against the 422 skills in SQLite database."""
    if not user_prompt:
        return []

    prompt_low = user_prompt.lower()
    words = [w for w in re.findall(r"[a-zA-Z0-9_\-]+", prompt_low) if len(w) > 2]
    if not words:
        return []

    try:
        conn = db_engine.get_db_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Check active skill first
        active = get_active_skill()
        matched = []
        if active:
            c.execute("SELECT * FROM agent_skills WHERE id = ?", (active["skill_id"],))
            row = c.fetchone()
            if row:
                matched.append(dict(row))

        # Check exact ID mentions
        for w in words:
            c.execute(
                "SELECT * FROM agent_skills WHERE LOWER(id) = ? OR LOWER(id) = ?",
                (w, w.replace("_", "-")),
            )
            rows = c.fetchall()
            for r in rows:
                d = dict(r)
                if not any(m["id"] == d["id"] for m in matched):
                    matched.append(d)

        # Keyword search
        for w in words[:4]:
            if len(matched) >= limit:
                break
            if w in [
                "the",
                "and",
                "for",
                "with",
                "how",
                "what",
                "can",
                "you",
                "use",
                "make",
                "build",
            ]:
                continue
            c.execute(
                "SELECT * FROM agent_skills WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ? LIMIT 2",
                (f"%{w}%", f"%{w}%"),
            )
            rows = c.fetchall()
            for r in rows:
                d = dict(r)
                if not any(m["id"] == d["id"] for m in matched):
                    matched.append(d)

        conn.close()
        return matched[:limit]
    except Exception as e:
        print("[AgentSkillRuntime] match error:", e)
        return []


def auto_select_skill(user_prompt, min_score=35):
    """
    Intelligently analyzes the user's task prompt and automatically selects
    the best matching specialized skill from the 422 skills arsenal.
    """
    if not user_prompt:
        return None, 0

    p_low = user_prompt.lower().strip()
    # Don't auto-select on trivial greetings, basic everyday PC commands or hardware controls
    everyday_stop_words = [
        "hi",
        "hello",
        "hey",
        "mute",
        "unmute",
        "volume",
        "sound",
        "brightness",
        "dim",
        "camera",
        "notepad",
        "calc",
        "calculator",
        "weather",
        "news",
        "jobs",
        "clear skill",
        "what is",
        "how are you",
        "who are you",
        "screenshot",
        "taskmgr",
        "task manager",
        "desktop",
        "downloads",
        "documents",
        "pictures",
        "videos",
        "music",
        "lock",
        "sleep",
    ]
    if any(
        p_low == w or p_low.startswith(w + " ") or f" {w} " in f" {p_low} "
        for w in everyday_stop_words
    ):
        return None, 0

    try:
        conn = db_engine.get_db_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT id, name, category, plugin, scope, description FROM agent_skills"
        )
        all_skills = [dict(r) for r in c.fetchall()]
        conn.close()
    except Exception as e:
        print("[AgentSkillRuntime] DB fetch error in auto_select_skill:", e)
        return None, 0

    p_words = set(re.findall(r"[a-zA-Z0-9_\-]+", p_low))
    best_skill = None
    max_score = 0

    for s in all_skills:
        score = 0
        s_id = s["id"].lower()
        s_name = s["name"].lower()
        desc = s["description"].lower()

        # Exact skill id match
        if s_id in p_low:
            score += 120

        # Cleaned id words
        clean_id_words = set(re.findall(r"[a-zA-Z0-9]+", s_id))
        common_id_words = clean_id_words.intersection(p_words)
        score += len(common_id_words) * 25

        # Skill name words match
        for w in re.findall(r"[a-zA-Z0-9]+", s_name):
            if len(w) > 2 and w in p_words:
                score += 15

        # Description words match
        for w in p_words:
            if len(w) > 3 and w in desc:
                score += 4

        # Specific domain boosts
        if ("flutter" in p_low or "dart" in p_low) and (
            "accessibility" in p_low
            or "a11y" in p_low
            or "tap target" in p_low
            or "contrast" in p_low
        ):
            if s_id == "flutter_a11y_agent":
                score += 100
        if "fastapi" in p_low and "fastapi" in s_id:
            score += 80
        if (
            "bash" in p_low
            and ("defensive" in p_low or "script" in p_low)
            and "bash" in s_id
        ):
            score += 80
        if ("threat" in p_low or "stride" in p_low) and (
            "threat" in s_id or "stride" in s_id
        ):
            score += 80
        if "airflow" in p_low and "airflow" in s_id:
            score += 80
        if ("postgres" in p_low or "postgresql" in p_low) and "postgres" in s_id:
            score += 80
        if ("k8s" in p_low or "kubernetes" in p_low) and (
            "k8s" in s_id or "kubernetes" in s_id
        ):
            score += 80
        if (
            "wcag" in p_low or "accessibility audit" in p_low
        ) and "accessibility" in s_id:
            score += 80
        if (
            "security audit" in p_low or "vulnerability" in p_low
        ) and "security-auditor" in s_id:
            score += 80
        if any(w in p_low for w in ["website", "web app", "html", "css", "frontend", "webpage", "portfolio"]):
            if s_id in ["frontend-developer", "web-architect", "modern-javascript-patterns"]:
                score += 120
        if any(w in p_low for w in ["python", "python script", "py script"]):
            if s_id in ["python-pro", "python-development-python-scaffold"]:
                score += 100

        if any(w in p_low for w in ["pic", "pic18f", "pickit", "pickit3", "pic18f85k22", "mcp9701", "trainer board", "embedded c"]):
            if s_id == "pic-embedded-engineer":
                score += 150


        if score > max_score:
            max_score = score
            best_skill = s

    if max_score >= min_score and best_skill:
        return best_skill, max_score
    return None, 0


def build_system_prompt_skill_injection(user_prompt):
    """
    Constructs a rich skills injection block to enrich the LLM system prompt.
    Automatically selects relevant skills or injects the active working skill ONLY
    if relevant to the current user prompt.
    """
    if not user_prompt:
        return ""

    p_low = user_prompt.lower().strip()

    # Check for everyday PC commands / casual greetings - NEVER inject developer skills into these!
    everyday_skip = [
        "volume",
        "sound",
        "mute",
        "unmute",
        "brightness",
        "dim",
        "calc",
        "calculator",
        "notepad",
        "screenshot",
        "taskmgr",
        "task manager",
        "settings",
        "paint",
        "explorer",
        "downloads",
        "documents",
        "desktop",
        "pictures",
        "videos",
        "music",
        "recycle bin",
        "lock pc",
        "sleep pc",
        "time",
        "date",
        "battery",
        "specs",
        "ram",
        "cpu",
        "ip address",
        "youtube",
        "google",
        "gmail",
        "github",
        "how are you",
        "what's up",
        "hey",
        "hello",
        "hi",
    ]
    if any(
        p_low == w or p_low.startswith(w + " ") or f" {w} " in f" {p_low} "
        for w in everyday_skip
    ):
        return ""

    skill = None
    # 1. Check auto-selected skill for the given task
    auto_s, score = auto_select_skill(user_prompt, min_score=35)
    if auto_s:
        skill = auto_s
        set_active_skill(auto_s["id"], auto_s["name"])
    else:
        # 2. Check active skill in session ONLY if prompt actually shares terms with the active skill!
        active = get_active_skill()
        if active:
            active_id = active.get("skill_id", "").lower()
            active_name = active.get("name", "").lower()
            id_words = set(re.findall(r"[a-zA-Z0-9]+", active_id + " " + active_name))
            prompt_words = set(re.findall(r"[a-zA-Z0-9]+", p_low))
            # Require at least one meaningful keyword overlap, or explicit "skill" mention
            if "skill" in p_low or any(
                w in id_words for w in prompt_words if len(w) > 3
            ):
                conn = db_engine.get_db_connection()
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute(
                    "SELECT * FROM agent_skills WHERE id = ?", (active["skill_id"],)
                )
                row = c.fetchone()
                conn.close()
                if row:
                    skill = dict(row)
            else:
                # Active skill has zero relation to this query - clear it to avoid stuck persona!
                clear_active_skill()

    if not skill:
        return ""

    content, file_path = get_skill_content(skill["id"])

    if content:
        clean_content = re.sub(
            r"^---\n.*?\n---\n", "", content, flags=re.DOTALL
        ).strip()
        snippet = clean_content[:15000]
        if len(clean_content) > 15000:
            snippet += "\n... [Full operational protocol loaded in memory]"
        extra_pic_directive = ""
        if skill["id"] == "pic-embedded-engineer":
            extra_pic_directive = """
CRITICAL EMBEDDED C CODE GENERATION RULES (PIC18F TRAINER 2 REV 1.24):
1. SINGLE COMPLETE CODE BLOCK: You MUST output the entire firmware as a SINGLE, UNIFIED, COMPLETE ```c``` code block starting with:
   #include <xc.h>
   #include <stdio.h>
   #include <stdint.h>
   all the way through 'void main(void)'. NEVER break or fragment the code into multiple snippets, numbered tutorial steps, or separate blocks.
2. EXACT CRYSTAL & CONFIG BITS:
   - Oscillator crystal is 4.9152 MHz: ALWAYS define '#define _XTAL_FREQ 4915200'. NEVER use 4 MHz or any other value!
   - Declare all 14 #pragma config directives (FOSC=HS2, SOSCSEL=DIG, WDTEN=OFF, MCLRE=ON, STVREN=ON).
3. LCD LINE 1 BROKEN DEFECT:
   - Line 1 of the 16x2 LCD is physically broken and unreadable on this trainer.
   - ALWAYS target Line 2 using 'LCD_Cmd(0xC0)' or 'LCD_Set_Cursor(2, 1)'. NEVER write to Line 1 (0x80).
4. SENSOR TRANSFER CHARACTERISTICS (MCP9701-E/TO):
   - Analog input is AN0 (RA0, Pin 24).
   - Transfer formula: Temp_C = (V_mV - 400.0f) / 19.5f, where V_mV = (adc_raw * 5000.0f) / 4095.0f.
   - Always use a 16-sample rolling noise average on ADC readings.
5. PERIPHERAL PIN DEFINITIONS (EXACT TRAINER 2 WIRING):
   - LCD Data Bus: Full 8-bit mode wired to PORTH (LATH[7:0], TRISH=0x00). NEVER write LCD data to PORTD!
   - LCD Control: RS = RE0 (LATEbits.LATE0, TRISEbits.TRISE0=0), EN = RE1 (LATEbits.LATE1, TRISEbits.TRISE1=0).
   - LCD Backlight: RA4 (TRISAbits.TRISA4=0, LATAbits.LATA4=0 turns Backlight ON). MUST BE 0!
   - LED Bar: 8 discrete LEDs on PORTD[7:0] (LATD, TRISD=0x00).
   - Piezo Buzzer: Driven on LATF / LATAbits.LATA5 / LATCbits.LATC3. (RA4 is reserved exclusively for LCD Backlight).
   - Keypad: Rows on PORTB[4:2] (RB2..RB4 inputs, INTCON2bits.RBPU=0), Columns on PORTC[2:0] (outputs).
6. LCD TEXT & FLOAT FORMATTING IN C:
   - In C, the modulo operator '%' cannot be used on float variables (causes compiler error: invalid operands to binary expression float and int).
   - Convert temperature to integer tenths and format with sprintf:
     int t_tenths = (int)(temp_c * 10.0f);
     int t_int = t_tenths / 10;
     int t_frac = t_tenths % 10;
     if (t_frac < 0) t_frac = -t_frac;
     char lcd_buf[17];
     sprintf(lcd_buf, "TEMP: %d.%d C [OK]", t_int, t_frac);
     LCD_Set_Cursor(2, 1);
     LCD_String(lcd_buf);
7. STANDARD WORKING 8-BIT LCD DRIVER REFERENCE:
   void LCD_Pulse_Enable(void) {
       LATEbits.LATE1 = 1;
       __delay_us(25);
       LATEbits.LATE1 = 0;
       __delay_us(25);
   }
   void LCD_Command(unsigned char cmd) {
       LATEbits.LATE0 = 0;
       LATH = cmd;
       __delay_us(5);
       LCD_Pulse_Enable();
       if (cmd == 0x01 || cmd == 0x02) {
           __delay_ms(3);
       } else {
           __delay_us(80);
       }
   }
   void LCD_Char(char data) {
       LATEbits.LATE0 = 1;
       LATH = (unsigned char)data;
       __delay_us(5);
       LCD_Pulse_Enable();
       __delay_us(60);
   }
   void LCD_String(const char *s) {
       while (*s) { LCD_Char(*s++); }
   }
   void LCD_Set_Cursor(unsigned char row, unsigned char col) {
       LCD_Command(0xC0 + (col - 1)); // Always Line 2 (0xC0)
   }
   void LCD_Init(void) {
       __delay_ms(100);
       TRISAbits.TRISA4 = 0;
       LATAbits.LATA4 = 0; // Turn ON LCD Backlight (Active Low)

       TRISH = 0x00;         // PORTH: D0..D7 data bus outputs
       TRISEbits.TRISE0 = 0; // RE0: RS output
       TRISEbits.TRISE1 = 0; // RE1: EN output

       // HD44780 8-Bit Sync Sequence
       LCD_Command(0x30); __delay_ms(10);
       LCD_Command(0x30); __delay_ms(2);
       LCD_Command(0x30); __delay_us(200);

       LCD_Command(0x38); __delay_us(100); // 8-bit, 2 lines, 5x8 font
       LCD_Command(0x08); __delay_us(100); // Display OFF
       LCD_Command(0x01); __delay_ms(3);   // Clear Display
       LCD_Command(0x06); __delay_us(100); // Auto increment cursor
       LCD_Command(0x0C); __delay_ms(2);   // Display ON, cursor off
   }
"""

        return f"""

===================================================================
⚡ AUTOMATICALLY SELECTED SKILL ENGAGED: {skill['name']} ({skill['id']})
Category: {skill['category']} | Plugin: {skill.get('plugin') or 'Core'}
You are now acting with the specialized mastery of this skill.
Follow these specialized engineering rules, standards, and patterns:
-------------------------------------------------------------------
{snippet}
{extra_pic_directive}
===================================================================
"""
    else:
        return f"""

===================================================================
⚡ AUTOMATICALLY SELECTED SKILL ENGAGED: {skill['name']} ({skill['id']})
Category: {skill['category']}
Directives: {skill['description']}
===================================================================
"""
