"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: DREAM MEMORY CONSOLIDATION ENGINE
===================================================================
Tier 2 Durable Knowledge Graph & Fine-Tuning Distillation Engine.

Consolidation Pipeline ("Nightly Machine Dreaming"):
1. Ingests volatile working session turns from Tier 1 Qdrant hot cache
   (or unconsolidated turns from PostgreSQL chat_messages).
2. Performs semantic distillation: extracts Named Entities (NER),
   factual observations, and bi-temporal relations.
3. Persists consolidated graph nodes into PostgreSQL durable storage
   (kg_entities, kg_observations, kg_relations, facts) via enhanced_kg.
4. Performs pre-flight secret/credential scrubbing and exports high-value
   dialogue pairs to LoRA fine-tuning format (dataset_fine_tune.jsonl).
5. Flushes processed working turns from volatile Qdrant hot cache and
   records consolidation audit event in PostgreSQL.
"""

import os
import re
import time
import json
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple

import db_engine
import qdrant_session_cache
from enhanced_knowledge_graph import enhanced_kg
import memory_engine
from security_rbac_engine import security_rbac

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DreamConsolidationEngine")

FINETUNE_DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset_fine_tune.jsonl")

# Canonical Known Hardware and Software Entities
KNOWN_ENTITIES = {
    "PIC18F85K22": ("MICROCONTROLLER", "Microchip 80-pin TQFP, 64KB Flash, 3.8KB RAM, 4.9152 MHz external crystal"),
    "PICKIT 3": ("DEBUGGER", "Microchip PICkit 3 Hardware In-Circuit Debugger/Programmer (BUR181916585)"),
    "MCP9701": ("SENSOR", "Microchip linear active thermistor on AN0 (19.5 mV/C slope, 400 mV offset at 0C)"),
    "16X2 LCD": ("DISPLAY", "16x2 HD44780 character LCD data bus on PORTH, control on RE0/RE1, backlight on RA4"),
    "SHARED_MEMORY": ("IPC", "Zero-copy shared memory frame buffer (deep_mjpeg_frame_buffer) eliminating camera mutex contention"),
    "QDRANT": ("VECTOR_DATABASE", "Tier 1 volatile hot session memory & vector cache via gRPC 6334"),
    "POSTGRESQL": ("RELATIONAL_DATABASE", "Tier 2 ACID durable relational storage & bi-temporal knowledge graph (deep_db)"),
    "FASTAPI": ("API_FRAMEWORK", "Low-latency asynchronous ASGI gateway for WebSocket and telemetry streaming"),
    "RAMADEEP SINGH": ("PERSON", "Autonomous Workstation Owner & Lead Systems Architect"),
    "D.E.E.P": ("AI_SYSTEM", "Dynamic Executive Enterprise Platform - Sovereign Autonomous Cockpit Intelligence"),
    "CHROME": ("APPLICATION", "Designated browser for interactive YouTube multimedia playback on PC Speakers")
}


_DREAM_DB_INITIALIZED = False

def init_db():
    """Initializes PostgreSQL tables required for Dream Consolidation tracking."""
    global _DREAM_DB_INITIALIZED
    if _DREAM_DB_INITIALIZED:
        return True

    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        
        # 1. Consolidation Audit Ledger
        c.execute("""
            CREATE TABLE IF NOT EXISTS dream_consolidation_log (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255),
                source VARCHAR(64),
                turn_count INT DEFAULT 0,
                entities_count INT DEFAULT 0,
                observations_count INT DEFAULT 0,
                relations_count INT DEFAULT 0,
                finetune_exported INT DEFAULT 0,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Add is_consolidated column to chat_messages only if it does not already exist
        c.execute("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'chat_messages' AND column_name = 'is_consolidated'
        """)
        if not c.fetchone():
            c.execute("""
                ALTER TABLE chat_messages
                ADD COLUMN IF NOT EXISTS is_consolidated BOOLEAN DEFAULT FALSE
            """)

        conn.commit()
        conn.close()
        _DREAM_DB_INITIALIZED = True
        logger.info("[DreamEngine] PostgreSQL consolidation schema verified.")
        return True
    except Exception as e:
        logger.error(f"[DreamEngine] init_db error: {e}")
        return False


def _scrub_secrets(text: str) -> str:
    """Scrubs passwords, tokens, API keys and credentials before fine-tuning export."""
    if not text:
        return ""
    scrubbed = text
    # Regex replacement for secret keys, tokens, passwords
    scrubbed = re.sub(
        r'(?:api[_-]?key|password|secret|token|private[_-]?key)\s*[:=]\s*["\']?[a-zA-Z0-9_\-\.]{8,}["\']?',
        "[REDACTED_SECRET]",
        scrubbed,
        flags=re.IGNORECASE
    )
    # Scrub Authorization Bearer tokens
    scrubbed = re.sub(
        r'Bearer\s+[a-zA-Z0-9_\-\.]{15,}',
        "Bearer [REDACTED_TOKEN]",
        scrubbed,
        flags=re.IGNORECASE
    )
    return scrubbed


def _extract_entities_from_text(text: str) -> List[Dict[str, str]]:
    """Extracts known and regex-matched entities from dialogue turn."""
    found_entities = []
    text_upper = text.upper()

    for ent_key, (ent_type, ent_desc) in KNOWN_ENTITIES.items():
        if ent_key in text_upper:
            # Canonical casing
            name = ent_key.title() if ent_type == "PERSON" else ent_key
            found_entities.append({
                "name": name,
                "entityType": ent_type,
                "description": ent_desc
            })

    # Pattern extraction for technical acronyms & hardware registers (e.g., PORTH, TRISB, AN0, ML-KEM)
    tech_patterns = re.findall(r'\b(PORT[A-J]|LAT[A-J]|TRIS[A-J]|AN[0-9]{1,2}|EEPROM|UART|I2C|SPI|DirectShow|MediaPipe)\b', text)
    for tp in set(tech_patterns):
        tp_upper = tp.upper()
        if not any(e["name"].upper() == tp_upper for e in found_entities):
            found_entities.append({
                "name": tp_upper,
                "entityType": "HARDWARE_SPEC" if tp_upper.startswith(("PORT", "LAT", "TRIS", "AN")) else "PROTOCOL",
                "description": f"Hardware/Protocol register specification: {tp_upper}"
            })

    return found_entities


def _extract_relations_from_text(text: str, entities: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Extracts semantic relations between identified entities."""
    relations = []
    ent_names = [e["name"].upper() for e in entities]
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    # Canonical relations
    if "PICKIT 3" in ent_names and "PIC18F85K22" in ent_names:
        relations.append({"from": "PICkit 3", "to": "PIC18F85K22", "relationType": "PROGRAMS", "confidence": 1.0})
    if "MCP9701" in ent_names and "PIC18F85K22" in ent_names:
        relations.append({"from": "MCP9701", "to": "PIC18F85K22", "relationType": "SENSES_FOR", "confidence": 1.0})
    if "D.E.E.P" in ent_names and "POSTGRESQL" in ent_names:
        relations.append({"from": "D.E.E.P", "to": "PostgreSQL", "relationType": "PERSISTS_DURABLE_GRAPH_TO", "confidence": 1.0})
    if "D.E.E.P" in ent_names and "QDRANT" in ent_names:
        relations.append({"from": "D.E.E.P", "to": "Qdrant", "relationType": "CACHES_HOT_SESSION_IN", "confidence": 1.0})
    if "D.E.E.P" in ent_names and "SHARED_MEMORY" in ent_names:
        relations.append({"from": "D.E.E.P", "to": "SHARED_MEMORY", "relationType": "INGESTS_VISION_VIA", "confidence": 1.0})
    if "RAMADEEP SINGH" in ent_names and "D.E.E.P" in ent_names:
        relations.append({"from": "Ramadeep Singh", "to": "D.E.E.P", "relationType": "COMMANDS_AND_DIRECTS", "confidence": 1.0})
    if "RAMADEEP SINGH" in ent_names and "CHROME" in ent_names:
        relations.append({"from": "Ramadeep Singh", "to": "Chrome", "relationType": "PREFERS_FOR_YOUTUBE", "confidence": 0.95})

    return relations


def _extract_observations(text: str) -> List[str]:
    """Distills concise, atomic factual assertions from dialogue text."""
    observations = []
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for s in sentences:
        s_clean = s.strip()
        # Filter out trivial conversational pleasantries
        if len(s_clean) < 15 or len(s_clean) > 300:
            continue
        lower_s = s_clean.lower()
        if any(greet in lower_s for greet in ["good morning", "good evening", "how can i assist", "hello", "thank you"]):
            continue
        # Capture sentences with technical or actionable keywords
        if any(kw in lower_s for kw in ["must", "configured", "wired", "slope", "port", "buffer", "lcd", "pin", "register", "crystal", "rule", "line 2", "broken"]):
            observations.append(s_clean)

    return observations[:5]  # Cap at top 5 most salient observations per turn


def fetch_turns_for_consolidation(
    session_id: Optional[str] = None,
    max_turns: int = 50
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Ingests dialogue turns for consolidation:
    1. First checks Tier 1 volatile Qdrant hot cache (gRPC 6334).
    2. If Qdrant cache has turns, returns those with source='qdrant'.
    3. If empty, falls back to unconsolidated records in PostgreSQL chat_messages table.
    """
    # 1. Check Tier 1 Qdrant Hot Session Cache
    try:
        q_cache = qdrant_session_cache.get_qdrant_cache()
        q_turns = q_cache.get_recent_session_turns(session_id=session_id, limit=max_turns)
        if q_turns:
            logger.info(f"[DreamEngine] Ingested {len(q_turns)} volatile turns from Tier 1 Qdrant hot cache.")
            return q_turns, "qdrant"
    except Exception as e:
        logger.warning(f"[DreamEngine] Qdrant session fetch note: {e}")

    # 2. Check Tier 2 PostgreSQL chat_messages
    try:
        init_db()
        conn = db_engine.get_db_connection()
        conn.row_factory = True
        c = conn.cursor()

        query = """
            SELECT id, chat_id, role, content, timestamp
            FROM chat_messages
            WHERE is_consolidated IS FALSE OR is_consolidated IS NULL
            ORDER BY id ASC
            LIMIT %s
        """
        c.execute(query, (max_turns,))
        rows = c.fetchall()
        conn.close()

        pg_turns = []
        for r in rows:
            pg_turns.append({
                "id": str(r["id"]),
                "session_id": r["chat_id"] or "default",
                "role": r["role"],
                "text": r["content"] or "",
                "timestamp": r["timestamp"] or time.time()
            })

        if pg_turns:
            logger.info(f"[DreamEngine] Ingested {len(pg_turns)} unconsolidated turns from PostgreSQL chat_messages.")
            return pg_turns, "postgres_chat_messages"

    except Exception as e:
        logger.error(f"[DreamEngine] PostgreSQL chat_messages fetch error: {e}")

    return [], "none"


def group_turns_into_dialogue_pairs(turns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Pairs adjacent user/assistant turns into prompt-response interactions."""
    pairs = []
    i = 0
    while i < len(turns):
        curr = turns[i]
        role = (curr.get("role") or "").lower()
        if role in ["user", "human"]:
            prompt = curr.get("text", "")
            response = ""
            resp_ids = [curr.get("id")]
            if i + 1 < len(turns):
                next_turn = turns[i + 1]
                next_role = (next_turn.get("role") or "").lower()
                if next_role in ["assistant", "ai", "system"]:
                    response = next_turn.get("text", "")
                    resp_ids.append(next_turn.get("id"))
                    i += 1
            if prompt and response:
                pairs.append({
                    "prompt": prompt,
                    "response": response,
                    "session_id": curr.get("session_id", "default"),
                    "turn_ids": resp_ids
                })
        i += 1
    return pairs


def distill_and_consolidate(
    session_id: Optional[str] = None,
    max_turns: int = 50,
    export_finetune: bool = True
) -> Dict[str, Any]:
    """
    Main Consolidation Routine:
    - Ingests turns from Qdrant hot cache or PostgreSQL chat_messages.
    - Extracts entities, observations, relations, and facts.
    - Persists nodes to PostgreSQL durable graph (kg_entities, kg_observations, kg_relations, facts).
    - Appends sanitized dialogue pairs to dataset_fine_tune.jsonl.
    - Flushes consolidated turns from Qdrant hot cache & marks chat_messages consolidated.
    """
    t_start = time.time()
    init_db()

    turns, source = fetch_turns_for_consolidation(session_id=session_id, max_turns=max_turns)
    if not turns:
        logger.info("[DreamEngine] No active un-consolidated memories found. System memory in steady state.")
        return {
            "success": True,
            "status": "steady_state",
            "message": "No new memories to consolidate",
            "source": source,
            "consolidated_turns": 0,
            "entities_created": 0,
            "observations_added": 0,
            "relations_created": 0,
            "facts_stored": 0,
            "finetune_exported": 0,
            "duration_seconds": round(time.time() - t_start, 4)
        }

    dialogue_pairs = group_turns_into_dialogue_pairs(turns)
    all_created_entities = []
    total_observations = 0
    all_created_relations = []
    total_facts = 0
    finetune_count = 0
    processed_turn_ids = []

    # 1. Distill Knowledge Graph Entities, Observations & Relations
    for turn in turns:
        text = turn.get("text", "")
        if not text or len(text.strip()) < 5:
            continue

        processed_turn_ids.append(turn.get("id"))

        # Extract entities
        entities = _extract_entities_from_text(text)
        if entities:
            res_ent = enhanced_kg.create_entities(entities)
            if res_ent.get("success"):
                all_created_entities.extend(res_ent.get("createdEntities", []))

            # Extract relations among entities
            relations = _extract_relations_from_text(text, entities)
            if relations:
                res_rel = enhanced_kg.create_relations(relations)
                if res_rel.get("success"):
                    all_created_relations.extend(res_rel.get("createdRelations", []))

            # Distill observations for primary entity
            obs_list = _extract_observations(text)
            if obs_list:
                primary_entity = entities[0]["name"]
                res_obs = enhanced_kg.add_observations(
                    entity_name=primary_entity,
                    observations=obs_list,
                    confidence=0.95,
                    source="dream_consolidation"
                )
                if res_obs.get("success"):
                    total_observations += res_obs.get("observationsAdded", 0)

                # Persist durable fact in memory_engine
                for single_obs in obs_list[:2]:
                    try:
                        memory_engine.store_fact(concept=primary_entity, facts=single_obs)
                        total_facts += 1
                    except Exception as fe:
                        logger.debug(f"[DreamEngine] Fact store notice: {fe}")

    # 2. Export Sanitized LoRA Fine-Tuning Dataset
    if export_finetune and dialogue_pairs:
        try:
            with open(FINETUNE_DATASET, "a", encoding="utf-8") as f:
                for pair in dialogue_pairs:
                    clean_prompt = _scrub_secrets(pair["prompt"])
                    clean_response = _scrub_secrets(pair["response"])

                    # Do not export empty or heavily corrupted turns
                    if len(clean_prompt) < 5 or len(clean_response) < 5:
                        continue

                    entry = {
                        "messages": [
                            {"role": "system", "content": "You are D.E.E.P Sovereign Autonomous Workstation AI."},
                            {"role": "user", "content": clean_prompt},
                            {"role": "assistant", "content": clean_response}
                        ],
                        "instruction": clean_prompt,
                        "context": "D.E.E.P Sovereign Autonomous Workstation Memory",
                        "response": clean_response
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    finetune_count += 1
            logger.info(f"[DreamEngine] Exported {finetune_count} sanitized pairs to {FINETUNE_DATASET}")
        except Exception as fte:
            logger.error(f"[DreamEngine] Fine-tuning export error: {fte}")

    # 3. Flushes volatile Qdrant hot cache or mark PostgreSQL records consolidated
    if source == "qdrant":
        try:
            q_cache = qdrant_session_cache.get_qdrant_cache()
            q_cache.clear_session_cache(session_id=session_id)
            logger.info(f"[DreamEngine] Flushed consolidated turns from Tier 1 Qdrant hot cache (session: {session_id or 'all'}).")
        except Exception as qce:
            logger.error(f"[DreamEngine] Qdrant cache clear error: {qce}")
    elif source == "postgres_chat_messages":
        try:
            valid_ids = [int(tid) for tid in processed_turn_ids if str(tid).isdigit()]
            if valid_ids:
                conn = db_engine.get_db_connection()
                c = conn.cursor()
                c.execute("UPDATE chat_messages SET is_consolidated = TRUE WHERE id = ANY(%s)", (valid_ids,))
                conn.commit()
                conn.close()
                logger.info(f"[DreamEngine] Marked {len(valid_ids)} chat_messages as consolidated in PostgreSQL.")
        except Exception as pge:
            logger.error(f"[DreamEngine] chat_messages consolidation mark error: {pge}")

    # 4. Audit Ledger Record in PostgreSQL
    duration = round(time.time() - t_start, 4)
    unique_entities = list(set(all_created_entities))
    unique_relations = list(set(all_created_relations))

    try:
        conn = db_engine.get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO dream_consolidation_log (
                session_id, source, turn_count, entities_count, observations_count,
                relations_count, finetune_exported, details
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id or "global",
            source,
            len(turns),
            len(unique_entities),
            total_observations,
            len(unique_relations),
            finetune_count,
            f"Consolidated in {duration}s. Entities: {', '.join(unique_entities[:5])}"
        ))
        conn.commit()
        conn.close()
    except Exception as ale:
        logger.warning(f"[DreamEngine] Audit ledger record warning: {ale}")

    telemetry = {
        "success": True,
        "status": "consolidated",
        "source": source,
        "session_id": session_id or "global",
        "consolidated_turns": len(turns),
        "dialogue_interactions": len(dialogue_pairs),
        "entities_created": len(unique_entities),
        "observations_added": total_observations,
        "relations_created": len(unique_relations),
        "facts_stored": total_facts,
        "finetune_exported": finetune_count,
        "duration_seconds": duration,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    logger.info(
        f"[DreamEngine] Consolidation complete: {len(turns)} turns -> "
        f"{len(unique_entities)} entities, {total_observations} observations, "
        f"{len(unique_relations)} relations, {finetune_count} fine-tune pairs in {duration}s."
    )
    return telemetry


def dream_cycle(session_id: Optional[str] = None, max_turns: int = 50, export_finetune: bool = True) -> Dict[str, Any]:
    """
    Executive entrypoint for Sleep-Phase Memory Replay ("Nightly Machine Dreaming").
    Maintains 100% backward compatibility with previous dream_cycle callers.
    """
    logger.info("Entering REM Sleep Phase (Nightly Machine Dreaming Consolidation)...")
    return distill_and_consolidate(
        session_id=session_id,
        max_turns=max_turns,
        export_finetune=export_finetune
    )


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("==================================================================")
    print("D.E.E.P SOVEREIGN AI: DREAM MEMORY CONSOLIDATION ENGINE")
    print("==================================================================")
    init_db()
    result = dream_cycle(max_turns=10)
    print("Result Summary:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("==================================================================")
