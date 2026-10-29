"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: TIERED MEMORY ENGINE
===================================================================
Tiered Memory Architecture:
- Tier 1 (Volatile / Hot): Qdrant vector session cache via gRPC 6334 for
  immediate conversational context and sub-millisecond semantic retrieval.
- Tier 2 (Durable / Persistent): PostgreSQL (deep_db) facts table +
  bi-temporal Knowledge Graph (kg_entities, kg_observations, kg_relations)
  for permanent transactional durability.
"""

import os
import re
import time
from typing import Any, Dict, List

import db_engine
import qdrant_session_cache
from enhanced_knowledge_graph import enhanced_kg

STOPWORDS = {
    "what",
    "is",
    "my",
    "the",
    "a",
    "an",
    "for",
    "to",
    "in",
    "of",
    "and",
    "or",
    "on",
    "with",
    "how",
    "show",
    "tell",
    "me",
    "about",
}


def get_connection():
    conn = db_engine.get_db_connection()
    conn.row_factory = True
    return conn


def store_fact(concept: str, facts: str) -> Dict[str, Any]:
    """
    Stores or updates knowledge across both tiers:
    1. Tier 2 (Durable): PostgreSQL facts ledger + Knowledge Graph observations.
    2. Tier 1 (Hot): Qdrant vector working memory via gRPC 6334.
    """
    try:
        concept_clean = concept.strip()
        facts_clean = facts.strip()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Tier 2: Durable PostgreSQL storage
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO facts (concept, facts, timestamp) VALUES (%s, %s, %s)
            ON CONFLICT (concept) DO UPDATE SET facts = EXCLUDED.facts, timestamp = EXCLUDED.timestamp
            """,
            (concept_clean, facts_clean, now),
        )
        cursor.execute("SELECT id FROM facts WHERE concept = %s", (concept_clean,))
        row = cursor.fetchone()
        fact_id = row["id"] if row else None
        conn.commit()
        conn.close()

        # 2. Tier 2: Durable Knowledge Graph observation
        try:
            enhanced_kg.add_observations(
                entity_name=concept_clean,
                observations=[facts_clean],
                confidence=1.0,
                source="memory_engine"
            )
        except Exception as kg_err:
            print(f"[MemoryEngine] KG sync notice: {kg_err}")

        # 3. Tier 1: Hot Qdrant Vector Cache (gRPC 6334)
        try:
            q_cache = qdrant_session_cache.get_qdrant_cache()
            q_cache.store_hot_fact(
                concept=concept_clean,
                fact=facts_clean,
                metadata={"fact_id": fact_id, "tier": 1}
            )
        except Exception as q_err:
            print(f"[MemoryEngine] Qdrant cache notice: {q_err}")

        return {
            "status": "success",
            "fact_id": fact_id,
            "concept": concept_clean,
            "facts": facts_clean,
            "message": f"Persisted knowledge: '{concept_clean}' into Tiered Memory (Qdrant gRPC + PostgreSQL Durable Graph).",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def recall_facts(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Recalls facts combining:
    - Tier 1: Qdrant Hot Session Vector Cache via gRPC 6334 (sub-millisecond semantic match)
    - Tier 2: PostgreSQL Durable Relational Facts Ledger + Knowledge Graph
    """
    try:
        combined_results = []
        seen_concepts = set()

        # 1. Fast Tier 1 Lookup: Qdrant Vector Cache
        try:
            q_cache = qdrant_session_cache.get_qdrant_cache()
            hot_hits = q_cache.recall_hot_facts(query, limit=limit)
            for hit in hot_hits:
                c = hit.get("concept", "")
                if c and c.lower() not in seen_concepts:
                    seen_concepts.add(c.lower())
                    combined_results.append({
                        "id": hit.get("id"),
                        "concept": c,
                        "facts": hit.get("facts", ""),
                        "timestamp": hit.get("timestamp", ""),
                        "tier": "Tier 1 (Qdrant Hot Cache)"
                    })
        except Exception as q_err:
            print(f"[MemoryRecall] Qdrant hot recall notice: {q_err}")

        # 2. Tier 2 Lookup: PostgreSQL Durable Facts Ledger
        tokens = [w.strip() for w in re.findall(r"\b[A-Za-z0-9_-]+\b", query.lower())]
        keywords = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

        if not keywords:
            keywords = [query.strip()]

        conn = get_connection()
        cursor = conn.cursor()

        clauses = []
        params = []
        for kw in keywords:
            clauses.append("(concept ILIKE %s OR facts ILIKE %s)")
            params.extend([f"%{kw}%", f"%{kw}%"])

        sql = f"""
            SELECT id, concept, facts, timestamp
            FROM facts
            WHERE {' OR '.join(clauses)}
            ORDER BY id DESC
            LIMIT %s
        """
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        for r in rows:
            c = r["concept"]
            if c and c.lower() not in seen_concepts:
                seen_concepts.add(c.lower())
                combined_results.append({
                    "id": r["id"],
                    "concept": c,
                    "facts": r["facts"],
                    "timestamp": str(r["timestamp"]),
                    "tier": "Tier 2 (PostgreSQL Durable Ledger)"
                })

        # 3. Tier 2 Supplementary Lookup: Knowledge Graph Observations if space remains
        if len(combined_results) < limit:
            try:
                kg_res = enhanced_kg.query_graph(
                    search_text=query,
                    min_confidence=0.5
                )
                if kg_res.get("success"):
                    for obs in kg_res.get("observations", []):
                        ent = obs.get("entity_name", "")
                        if ent and ent.lower() not in seen_concepts:
                            seen_concepts.add(ent.lower())
                            combined_results.append({
                                "id": obs.get("id"),
                                "concept": ent,
                                "facts": obs.get("observation_text", ""),
                                "timestamp": obs.get("created_at", ""),
                                "tier": "Tier 2 (PostgreSQL Durable Graph)"
                            })
                            if len(combined_results) >= limit:
                                break
            except Exception as kg_err:
                print(f"[MemoryRecall] KG supplementary recall notice: {kg_err}")

        return combined_results[:limit]
    except Exception as e:
        print(f"[MemoryRecallError]: {e}")
        return []


def list_all_facts(limit: int = 25) -> List[Dict[str, Any]]:
    """Lists durable facts directly from PostgreSQL ledger."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, concept, facts, timestamp FROM facts ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r["id"],
                "concept": r["concept"],
                "facts": r["facts"],
                "timestamp": str(r["timestamp"]),
                "tier": "Tier 2 (PostgreSQL Durable Ledger)"
            }
            for r in rows
        ]
    except Exception:
        return []
