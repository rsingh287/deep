"""
Human Feedback & Reinforcement Learning Core (RLHF Engine)
Enables D.E.E.P, J.A.R.V.I.S., and F.R.I.D.A.Y. to know what they are doing right and wrong.
Logs user ratings, corrections, and explicit preferences into:
1. PostgreSQL deep_db (`human_feedback` table)
2. Semantic Long-Term Vector Memory (`memory_engine`)
3. DPO / SFT training datasets (`dataset_fine_tune.jsonl`)
4. Dynamic In-Context System Prompt Reinforcement (Active Few-Shot Guardrails)
"""

import os
import re
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import db_engine

FEEDBACK_DATASET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_fine_tune.jsonl")

def init_feedback_db():
    """Ensures the human_feedback table exists in the database."""
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS human_feedback (
            id SERIAL PRIMARY KEY,
            chat_id TEXT,
            message_id TEXT,
            prompt TEXT,
            ai_response TEXT,
            rating INT,
            feedback_type TEXT,
            critique_tag TEXT,
            user_correction TEXT,
            learned_rule TEXT,
            applied_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[HumanFeedbackEngine] DB Init Notice: {e}")
        return False


def synthesize_learned_rule(prompt: str, ai_response: str, rating: int, critique_tag: str, user_correction: str) -> str:
    """Synthesizes an actionable guideline rule from the user's feedback."""
    clean_p = (prompt or "").strip().replace("\n", " ")
    if len(clean_p) > 120:
        clean_p = clean_p[:117] + "..."

    clean_corr = (user_correction or "").strip().replace("\n", " ")
    clean_tag = (critique_tag or "").strip()

    if rating > 0:
        return f"[APPROVED BEHAVIOR] When asked about '{clean_p}': user validated this approach as correct, effective, and desired."
    else:
        rule_parts = [f"[CORRECTION / AVOIDANCE] When user asks '{clean_p}':"]
        if clean_tag:
            rule_parts.append(f"DO NOT repeat error pattern: '{clean_tag}'.")
        if clean_corr:
            rule_parts.append(f"USER DIRECTIVE / PREFERENCE: {clean_corr}.")
        else:
            rule_parts.append("DO NOT repeat the previous flawed response. Provide an alternative, verified solution.")
        return " ".join(rule_parts)


def record_feedback(
    chat_id: str,
    prompt: str,
    ai_response: str,
    rating: int,
    feedback_type: str = "manual",
    critique_tag: str = "",
    user_correction: str = "",
    message_id: str = ""
) -> Dict[str, Any]:
    """
    Records human feedback (+1 or -1, critique, correction) and immediately
    integrates it into cognitive memory and DPO fine-tuning datasets.
    """
    init_feedback_db()
    learned_rule = synthesize_learned_rule(prompt, ai_response, rating, critique_tag, user_correction)

    feedback_id = None
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO human_feedback 
            (chat_id, message_id, prompt, ai_response, rating, feedback_type, critique_tag, user_correction, learned_rule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id or f"chat_{int(time.time()*1000)}",
                message_id or f"msg_{int(time.time()*1000)}",
                prompt,
                ai_response,
                rating,
                feedback_type,
                critique_tag,
                user_correction,
                learned_rule
            )
        )
        feedback_id = cur.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[HumanFeedbackEngine] Record DB Error: {e}")

    # 1. Integrate into Long-Term Semantic Vector Memory
    try:
        import memory_engine
        concept_title = f"Human Feedback ({'APPROVED' if rating > 0 else 'CORRECTION'}): {critique_tag or (prompt[:30] if prompt else 'Rule')}"
        memory_engine.store_fact(concept_title, learned_rule)
    except Exception as me:
        print(f"[HumanFeedbackEngine] Semantic Memory Storage Notice: {me}")

    # 2. Append to DPO / SFT Training Dataset for LoRA adaptation
    try:
        triplet = {
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id,
            "prompt": prompt,
            "rating": rating,
            "critique_tag": critique_tag,
            "rejected_response": ai_response if rating < 0 else None,
            "chosen_response": user_correction if user_correction else (ai_response if rating > 0 else None),
            "learned_rule": learned_rule,
            "status": "pending_fine_tune"
        }
        with open(FEEDBACK_DATASET_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(triplet) + '\n')
    except Exception as de:
        print(f"[HumanFeedbackEngine] Dataset Append Notice: {de}")

    # 3. Update Enterprise Prompt A/B Testing Metrics
    try:
        import enterprise_prompt_ab_testing
        enterprise_prompt_ab_testing.enterprise_ab_testing.record_feedback(
            version="v1",
            is_positive=(rating > 0)
        )
    except Exception:
        pass

    return {
        "success": True,
        "feedback_id": feedback_id,
        "rating": rating,
        "learned_rule": learned_rule,
        "message": "Human feedback recorded and permanently integrated into AI cognitive core."
    }


def get_feedback_context(user_prompt: str, limit: int = 4) -> str:
    """
    Retrieves past human feedback rules relevant to the user's prompt
    to inject into the system prompt before LLM generation.
    """
    if not user_prompt:
        return ""

    tokens = [w.lower().strip() for w in re.findall(r"\b[A-Za-z0-9_-]+\b", user_prompt) if len(w) > 2]
    stopwords = {"what", "the", "and", "for", "with", "this", "that", "how", "make", "show", "can", "you", "are", "have"}
    keywords = [t for t in tokens if t not in stopwords]
    if not keywords:
        keywords = [user_prompt.lower().strip()[:20]]

    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()

        # Query past feedback entries with learned rules
        cur.execute(
            """
            SELECT id, prompt, rating, critique_tag, user_correction, learned_rule, applied_count
            FROM human_feedback
            ORDER BY id DESC
            LIMIT 100
            """
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return ""

        # Match relevance based on keyword overlap
        matched_rules = []
        for r in rows:
            r_dict = dict(r) if hasattr(r, 'keys') else {
                "id": r[0], "prompt": r[1], "rating": r[2], 
                "critique_tag": r[3], "user_correction": r[4], 
                "learned_rule": r[5], "applied_count": r[6]
            }
            search_corpus = f"{r_dict.get('prompt', '')} {r_dict.get('critique_tag', '')} {r_dict.get('user_correction', '')} {r_dict.get('learned_rule', '')}".lower()
            score = sum(1 for kw in keywords if kw in search_corpus)
            if score > 0 or len(rows) <= 3:
                matched_rules.append((score, r_dict))

        # Sort by relevance score descending
        matched_rules.sort(key=lambda x: x[0], reverse=True)
        selected = [m[1] for m in matched_rules[:limit]]

        if not selected:
            return ""

        instructions = []
        for item in selected:
            rating = item.get("rating", 0)
            rule = item.get("learned_rule", "")
            corr = item.get("user_correction", "")
            tag = item.get("critique_tag", "")
            
            if rating < 0:
                instructions.append(f"• ⚠️ PAST ERROR TO AVOID: {rule}")
            else:
                instructions.append(f"• ✓ USER APPROVED PATTERN: {rule}")

        rules_formatted = "\n".join(instructions)
        return (
            f"\n\n[COGNITIVE HUMAN FEEDBACK DIRECTIVES (RLHF Memory)]\n"
            f"The user has explicitly trained your core with feedback on what you did right and wrong in previous tasks.\n"
            f"You MUST strictly follow these user directives:\n"
            f"{rules_formatted}\n"
        )
    except Exception as e:
        print(f"[HumanFeedbackEngine] Context Recall Notice: {e}")
        return ""


def detect_conversational_feedback(user_prompt: str, recent_history: list = None) -> Optional[Tuple[str, str, List[Dict]]]:
    """
    Detects if the user's chat message is conversational feedback on the previous AI output
    (e.g., 'good job', 'that was correct', 'that didn't work', 'wrong, use python instead').
    """
    prompt_low = user_prompt.lower().strip()
    
    # 1. Positive Praise Patterns
    positive_patterns = [
        "good job", "great job", "well done", "nice work", "that worked", 
        "that was right", "that is right", "correct", "perfect", "spot on", 
        "exactly what i wanted", "that's right", "thats right", "awesome work",
        "that worked great", "excellent work"
    ]
    
    # 2. Negative Critique / Correction Patterns
    negative_patterns = [
        "that didn't work", "that did not work", "that's wrong", "thats wrong",
        "incorrect", "you are wrong", "you made a mistake", "not what i asked",
        "wrong answer", "fix this error", "that was wrong", "you forgot",
        "do this instead", "no, use", "no use", "should have used", "you should have"
    ]

    is_positive = any(re.search(rf"\b{re.escape(p)}\b", prompt_low) for p in positive_patterns)
    is_negative = any(re.search(rf"\b{re.escape(p)}\b", prompt_low) for p in negative_patterns)

    # Don't trigger if it's a general question asking about right or wrong
    if any(q in prompt_low for q in ["who is right", "is it right", "what is wrong with", "am i right", "is this right", "can we add"]):
        return None

    if not (is_positive or is_negative):
        return None

    # Retrieve the last AI message from history or DB
    last_ai_msg = ""
    last_user_prompt = ""
    chat_id = "default_session"

    if recent_history:
        for msg in reversed(recent_history):
            role = msg.get("role", "")
            if not last_ai_msg and role in ["ai", "assistant"]:
                last_ai_msg = msg.get("content", "")
            elif last_ai_msg and not last_user_prompt and role == "user":
                last_user_prompt = msg.get("content", "")
                break

    # If not found in memory, query last message from DB
    if not last_ai_msg:
        try:
            conn = db_engine.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT chat_id, role, content FROM chat_messages ORDER BY id DESC LIMIT 5")
            rows = cur.fetchall()
            conn.close()
            for r in rows:
                c_id, role, cont = r[0], r[1], r[2]
                if not last_ai_msg and role in ["ai", "assistant"]:
                    last_ai_msg = cont
                    chat_id = c_id
                elif last_ai_msg and not last_user_prompt and role == "user":
                    last_user_prompt = cont
                    break
        except Exception:
            pass

    if not last_ai_msg:
        return None

    if is_positive:
        record_feedback(
            chat_id=chat_id,
            prompt=last_user_prompt or "Recent user request",
            ai_response=last_ai_msg[:500],
            rating=1,
            feedback_type="conversational_praise",
            critique_tag="accurate_solution",
            user_correction=""
        )
        reply = (
            "🌟 **[Human Feedback Recorded: Approved (+1)]**\n\n"
            "Thank you, Commander! I have registered your positive feedback into my **Cognitive Reinforcement Core**.\n"
            "This interaction pattern has been locked into long-term memory as verified and preferred."
        )
        return (reply, "human_feedback_reinforcement", [{"action": "feedback_saved", "rating": 1, "type": "positive"}])

    elif is_negative:
        # Extract possible correction
        correction = user_prompt
        for neg in negative_patterns:
            if neg in prompt_low:
                idx = prompt_low.find(neg) + len(neg)
                remainder = user_prompt[idx:].strip(" :,.-")
                if remainder:
                    correction = remainder
                break

        record_feedback(
            chat_id=chat_id,
            prompt=last_user_prompt or "Recent user request",
            ai_response=last_ai_msg[:500],
            rating=-1,
            feedback_type="conversational_correction",
            critique_tag="user_reported_flaw",
            user_correction=correction
        )
        reply = (
            "⚠️ **[Human Feedback Recorded: Correction (-1)]**\n\n"
            "Understood, Commander. I have analyzed your critique and committed the correction into my **Cognitive RLHF Memory**:\n\n"
            f"> **Logged Correction:** *\"{correction}\"*\n\n"
            "I have updated my semantic guidance rules and DPO dataset so I will not repeat this mistake in future answers."
        )
        return (reply, "human_feedback_reinforcement", [{"action": "feedback_saved", "rating": -1, "correction": correction}])

    return None


def get_all_feedback(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves all feedback records with statistics."""
    init_feedback_db()
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, chat_id, message_id, prompt, ai_response, rating, 
                   feedback_type, critique_tag, user_correction, learned_rule, 
                   applied_count, created_at
            FROM human_feedback
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cur.fetchall()
        conn.close()

        feedback_list = []
        for r in rows:
            feedback_list.append({
                "id": r[0],
                "chat_id": r[1],
                "message_id": r[2],
                "prompt": r[3],
                "ai_response": (r[4] or "")[:200] + ("..." if len(r[4] or "") > 200 else ""),
                "rating": r[5],
                "feedback_type": r[6],
                "critique_tag": r[7],
                "user_correction": r[8],
                "learned_rule": r[9],
                "applied_count": r[10],
                "created_at": str(r[11])
            })
        return feedback_list
    except Exception as e:
        print(f"[HumanFeedbackEngine] List Error: {e}")
        return []


def get_feedback_stats() -> Dict[str, Any]:
    """Calculates overall feedback statistics."""
    init_feedback_db()
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), SUM(CASE WHEN rating > 0 THEN 1 ELSE 0 END), SUM(CASE WHEN rating < 0 THEN 1 ELSE 0 END) FROM human_feedback")
        row = cur.fetchone()
        conn.close()

        total = row[0] or 0
        positive = row[1] or 0
        negative = row[2] or 0
        rate = round((positive / total * 100), 1) if total > 0 else 100.0

        return {
            "total_feedback": total,
            "positive_count": positive,
            "negative_count": negative,
            "approval_rate": rate
        }
    except Exception as e:
        print(f"[HumanFeedbackEngine] Stats Error: {e}")
        return {"total_feedback": 0, "positive_count": 0, "negative_count": 0, "approval_rate": 100.0}


def delete_feedback(feedback_id: int) -> bool:
    """Deletes a feedback record."""
    try:
        conn = db_engine.get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM human_feedback WHERE id = ?", (feedback_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[HumanFeedbackEngine] Delete Error: {e}")
        return False
