"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: QDRANT HOT SESSION CACHE (TIER 1)
===================================================================
Ultra-low-latency vector cache & working session memory powered by Qdrant
via gRPC port 6334.

Tier Separation:
- Tier 1 (Volatile / Hot): Qdrant via gRPC 6334 for immediate conversation
  session caching, prompt similarity, and sub-millisecond semantic retrieval.
- Tier 2 (Durable / Persistent): PostgreSQL (deep_db) for relational facts,
  bi-temporal knowledge graph, and long-term audit ledger.
"""

import os
import time
import uuid
import hashlib
import logging
import requests
from typing import List, Dict, Any, Optional

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    qmodels = None

logger = logging.getLogger("QdrantSessionCache")

# Default Configuration
DEFAULT_QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
DEFAULT_QDRANT_REST_PORT = int(os.getenv("QDRANT_REST_PORT", "6333"))
DEFAULT_QDRANT_GRPC_PORT = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
COLLECTION_HOT_SESSION = "hot_session_cache"
VECTOR_DIMENSION = 768  # Standard nomic-embed-text dimension


def _generate_fallback_embedding(text: str, dim: int = VECTOR_DIMENSION) -> List[float]:
    """Generates a deterministic normalized pseudo-semantic vector if Ollama is unreachable."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vec = []
    for i in range(dim):
        byte_val = h[i % len(h)]
        val = ((byte_val / 255.0) * 2.0) - 1.0
        vec.append(round(val, 6))
    # Normalize to unit length for cosine distance
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


_OLLAMA_AVAILABLE: Optional[bool] = None
_LAST_OLLAMA_CHECK: float = 0.0


def _is_ollama_alive() -> bool:
    """Checks whether local Ollama embedding service is actively listening."""
    global _OLLAMA_AVAILABLE, _LAST_OLLAMA_CHECK
    now = time.time()
    if _OLLAMA_AVAILABLE is not None and (now - _LAST_OLLAMA_CHECK < 10.0):
        return _OLLAMA_AVAILABLE
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.05)
        _OLLAMA_AVAILABLE = (s.connect_ex(("localhost", 11434)) == 0)
        s.close()
    except Exception:
        _OLLAMA_AVAILABLE = False
    _LAST_OLLAMA_CHECK = now
    return _OLLAMA_AVAILABLE


def get_embedding(text: str) -> List[float]:
    """Fetches embedding from Ollama nomic-embed-text or falls back cleanly in 0ms."""
    if _is_ollama_alive():
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        try:
            res = requests.post(
                f"{ollama_host}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=1.5
            )
            if res.status_code == 200:
                emb = res.json().get("embedding", [])
                if emb and len(emb) == VECTOR_DIMENSION:
                    return emb
        except Exception:
            pass
    return _generate_fallback_embedding(text, VECTOR_DIMENSION)


class QdrantSessionCache:
    """
    Tier 1 Hot Session Memory & Vector Cache.
    Prefers Qdrant gRPC (port 6334) with transparent in-memory fallback
    to prevent application stalls when Docker / Qdrant daemon is offline.
    """

    def __init__(
        self,
        host: str = DEFAULT_QDRANT_HOST,
        grpc_port: int = DEFAULT_QDRANT_GRPC_PORT,
        rest_port: int = DEFAULT_QDRANT_REST_PORT,
        collection_name: str = COLLECTION_HOT_SESSION,
        force_memory: bool = False
    ):
        self.host = host
        self.grpc_port = grpc_port
        self.rest_port = rest_port
        self.collection_name = collection_name
        self.client = None
        self.is_grpc_active = False
        self.is_memory_mode = False

        if not HAS_QDRANT:
            logger.warning("[QdrantCache] qdrant-client not installed.")
            return

        if force_memory:
            self._init_memory_client()
        else:
            self._init_grpc_client()

    def _init_grpc_client(self):
        """Attempts connection to live Qdrant service via gRPC port 6334."""
        import socket
        try:
            # Fast socket probe to avoid blocking event loops or worker threads
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex((self.host, self.grpc_port))
            sock.close()
            if result != 0:
                # Port is not listening; skip remote init immediately
                logger.info(f"[QdrantCache] gRPC port {self.grpc_port} not listening. Initializing in-memory volatile cache (Zero-Crash Fallback).")
                self._init_memory_client()
                return

            client = QdrantClient(
                host=self.host,
                port=self.rest_port,
                grpc_port=self.grpc_port,
                prefer_grpc=True,
                check_compatibility=False,
                timeout=2
            )
            client.get_collections()
            self.client = client
            self.is_grpc_active = True
            self.is_memory_mode = False
            self._ensure_collection()
            logger.info(f"[QdrantCache] Connected via gRPC to {self.host}:{self.grpc_port} (Collection: {self.collection_name})")
        except Exception as e:
            logger.info(f"[QdrantCache] Qdrant gRPC connection failed ({e}). Initializing in-memory volatile cache (Zero-Crash Fallback).")
            self._init_memory_client()

    def _init_memory_client(self):
        """Initializes volatile in-memory Qdrant client."""
        try:
            self.client = QdrantClient(":memory:")
            self.is_grpc_active = False
            self.is_memory_mode = True
            self._ensure_collection()
            logger.info(f"[QdrantCache] In-memory volatile cache active (Collection: {self.collection_name})")
        except Exception as e:
            logger.error(f"[QdrantCache] Failed to initialize in-memory Qdrant: {e}")
            self.client = None

    def _ensure_collection(self):
        """Creates the session collection if it does not already exist."""
        if not self.client or not qmodels:
            return
        try:
            existing = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in existing:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=qmodels.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.warning(f"[QdrantCache] Collection setup warning: {e}")

    def cache_session_turn(
        self,
        session_id: str,
        role: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Stores a dialogue turn into Tier 1 hot cache with vector embedding."""
        if not self.client:
            return ""

        point_id = str(uuid.uuid4())
        emb = get_embedding(text)
        payload = {
            "session_id": session_id,
            "role": role,
            "text": text,
            "timestamp": time.time(),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if metadata:
            payload.update(metadata)

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qmodels.PointStruct(
                        id=point_id,
                        vector=emb,
                        payload=payload
                    )
                ]
            )
            return point_id
        except Exception as e:
            logger.error(f"[QdrantCache] Upsert error: {e}")
            return ""

    def get_recent_session_turns(
        self,
        session_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieves dialogue turns from Tier 1 hot cache for distillation and consolidation."""
        if not self.client:
            return []

        filter_query = None
        if session_id and qmodels:
            filter_query = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="session_id",
                        match=qmodels.MatchValue(value=session_id)
                    )
                ]
            )

        try:
            if hasattr(self.client, "scroll"):
                res, _ = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_query,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                points = res
            else:
                return []

            turns = []
            for p in points:
                payload = p.payload or {}
                turns.append({
                    "id": str(p.id),
                    "session_id": payload.get("session_id", ""),
                    "role": payload.get("role", ""),
                    "text": payload.get("text", ""),
                    "timestamp": payload.get("timestamp", 0.0),
                    "created_at": payload.get("created_at", ""),
                    "metadata": payload
                })
            turns.sort(key=lambda t: t.get("timestamp", 0.0))
            return turns
        except Exception as e:
            logger.error(f"[QdrantCache] Get recent session turns error: {e}")
            return []

    def search_session_cache(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches hot session cache for semantically relevant recent context."""
        if not self.client:
            return []

        emb = get_embedding(query)
        filter_query = None
        if session_id and qmodels:
            filter_query = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="session_id",
                        match=qmodels.MatchValue(value=session_id)
                    )
                ]
            )

        try:
            # query_points handles both v1.x and newer Qdrant API
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=emb,
                    query_filter=filter_query,
                    limit=limit
                )
                points = res.points if hasattr(res, "points") else res
            else:
                points = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=emb,
                    query_filter=filter_query,
                    limit=limit
                )

            hits = []
            for p in points:
                hits.append({
                    "id": str(p.id),
                    "score": float(p.score),
                    "text": p.payload.get("text", "") if p.payload else "",
                    "role": p.payload.get("role", "") if p.payload else "",
                    "session_id": p.payload.get("session_id", "") if p.payload else "",
                    "timestamp": p.payload.get("timestamp", 0) if p.payload else 0,
                    "metadata": p.payload or {}
                })
            return hits
        except Exception as e:
            logger.error(f"[QdrantCache] Search error: {e}")
            return []

    def store_hot_fact(self, concept: str, fact: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Caches an active concept/fact in volatile working memory for instant lookup."""
        if not self.client:
            return False

        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"fact:{concept.strip().lower()}"))
        emb = get_embedding(f"{concept}: {fact}")
        payload = {
            "type": "fact",
            "concept": concept.strip(),
            "facts": fact.strip(),
            "text": f"{concept}: {fact}",
            "timestamp": time.time(),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if metadata:
            payload.update(metadata)

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qmodels.PointStruct(
                        id=point_id,
                        vector=emb,
                        payload=payload
                    )
                ]
            )
            return True
        except Exception as e:
            logger.error(f"[QdrantCache] Store hot fact error: {e}")
            return False

    def recall_hot_facts(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recalls facts from volatile working memory."""
        if not self.client:
            return []

        emb = get_embedding(query)
        filter_query = None
        if qmodels:
            filter_query = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="type",
                        match=qmodels.MatchValue(value="fact")
                    )
                ]
            )

        try:
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection_name,
                    query=emb,
                    query_filter=filter_query,
                    limit=limit
                )
                points = res.points if hasattr(res, "points") else res
            else:
                points = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=emb,
                    query_filter=filter_query,
                    limit=limit
                )

            results = []
            for p in points:
                payload = p.payload or {}
                results.append({
                    "id": str(p.id),
                    "score": float(p.score),
                    "concept": payload.get("concept", ""),
                    "facts": payload.get("facts", ""),
                    "timestamp": payload.get("created_at", "")
                })
            return results
        except Exception as e:
            logger.error(f"[QdrantCache] Recall hot facts error: {e}")
            return []

    def clear_session_cache(self, session_id: Optional[str] = None) -> bool:
        """Clears entries for a specific session or wipes the entire volatile collection."""
        if not self.client or not qmodels:
            return False
        try:
            if session_id:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=qmodels.FilterSelector(
                        filter=qmodels.Filter(
                            must=[
                                qmodels.FieldCondition(
                                    key="session_id",
                                    match=qmodels.MatchValue(value=session_id)
                                )
                            ]
                        )
                    )
                )
            else:
                self.client.delete_collection(self.collection_name)
                self._ensure_collection()
            return True
        except Exception as e:
            logger.error(f"[QdrantCache] Clear cache error: {e}")
            return False

    def get_tier_status(self) -> Dict[str, Any]:
        """Returns Tier 1 status and telemetry."""
        count = 0
        if self.client:
            try:
                info = self.client.get_collection(self.collection_name)
                count = info.points_count if hasattr(info, "points_count") else 0
            except Exception:
                count = 0

        return {
            "tier": 1,
            "role": "Hot Session Cache & Working Vector Memory",
            "backend": "gRPC" if self.is_grpc_active else "In-Memory Fallback",
            "grpc_port": self.grpc_port,
            "is_grpc_active": self.is_grpc_active,
            "is_memory_mode": self.is_memory_mode,
            "collection": self.collection_name,
            "cached_points": count,
            "vector_dimension": VECTOR_DIMENSION
        }


# Global singleton instance
_qdrant_cache = None


def get_qdrant_cache() -> QdrantSessionCache:
    """Returns singleton instance of Tier 1 Qdrant Hot Session Cache."""
    global _qdrant_cache
    if _qdrant_cache is None:
        _qdrant_cache = QdrantSessionCache()
    return _qdrant_cache
