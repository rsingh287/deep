"""
Memory Engine for Antigravity Local AI PC Cockpit (Jarvis Tier)
Persistent memory and fact store connected to memory.db with smart keyword search.
"""

import os
import re
import time
import requests
from typing import Any, Dict, List

import db_engine

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
    # Setting row_factory triggers db_engine.PostgresConnectionAdapter to use DictCursor
    conn.row_factory = True
    return conn


try:
    import chromadb
except Exception:
    chromadb = None

def get_chroma_collection():
    if not chromadb:
        return None
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
        client = chromadb.PersistentClient(path=db_path)
        return client.get_or_create_collection(name="long_term_memory")
    except Exception as e:
        print(f"[ChromaDB Init Error]: {e}")
        return None

def get_ollama_embedding(text: str):
    try:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        res = requests.post(f"{host}/api/embeddings", json={"model": "nomic-embed-text", "prompt": text}, timeout=10)
        if res.status_code == 200:
            return res.json().get("embedding", [])
    except Exception as e:
        print(f"[Ollama Embedding Error]: {e}")
    return []

def store_fact(concept: str, facts: str) -> Dict[str, Any]:
    """Stores or updates a persistent concept and fact in PostgreSQL and ChromaDB."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO facts (concept, facts, timestamp) VALUES (%s, %s, %s)
            ON CONFLICT (concept) DO UPDATE SET facts = EXCLUDED.facts, timestamp = EXCLUDED.timestamp
            """,
            (concept.strip(), facts.strip(), now),
        )
        # Fetch the id of the upserted row
        cursor.execute("SELECT id FROM facts WHERE concept = %s", (concept.strip(),))
        row = cursor.fetchone()
        fact_id = row["id"] if row else None
        conn.commit()
        conn.close()
        
        # Add to ChromaDB vector store
        collection = get_chroma_collection()
        if collection:
            embedding = get_ollama_embedding(concept + "\n" + facts)
            if embedding:
                collection.upsert(
                    documents=[facts],
                    metadatas=[{"concept": concept, "timestamp": now}],
                    ids=[str(fact_id)],
                    embeddings=[embedding]
                )

        return {
            "status": "success",
            "fact_id": fact_id,
            "concept": concept,
            "facts": facts,
            "message": f"Persisted knowledge: '{concept}' into semantic memory.",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def recall_facts(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Searches memory for relevant facts using Semantic RAG and nomic-embed-text."""
    try:
        # NOTE: Disabled ChromaDB semantic search on every query to prevent Ollama
        # from thrashing models in VRAM (swapping between nomic-embed-text and the LLM)
        # which causes massive 5-10 second delays per message.
        # collection = get_chroma_collection()
        # if collection:
        #     query_embedding = get_ollama_embedding(query)
        #     if query_embedding:
        #         results = collection.query(
        #             query_embeddings=[query_embedding],
        #             n_results=limit
        #         )
        #         if results and results["ids"] and results["ids"][0]:
        #             rag_results = []
        #             for idx, doc_id in enumerate(results["ids"][0]):
        #                 rag_results.append({
        #                     "id": doc_id,
        #                     "concept": results["metadatas"][0][idx].get("concept", ""),
        #                     "facts": results["documents"][0][idx],
        #                     "timestamp": results["metadatas"][0][idx].get("timestamp", "")
        #                 })
        #             return rag_results

        # Fallback to PostgreSQL exact keyword search if Chroma fails
        conn = get_connection()
        cursor = conn.cursor()

        tokens = [w.strip() for w in re.findall(r"\b[A-Za-z0-9_-]+\b", query.lower())]
        keywords = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

        if not keywords:
            keywords = [query.strip()]

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

        return [
            {
                "id": r["id"],
                "concept": r["concept"],
                "facts": r["facts"],
                "timestamp": str(r["timestamp"]),
            }
            for r in rows
        ]
    except Exception as e:
        print(f"[MemoryRecallError]: {e}")
        return []


def list_all_facts(limit: int = 25) -> List[Dict[str, Any]]:
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
            }
            for r in rows
        ]
    except Exception:
        return []
