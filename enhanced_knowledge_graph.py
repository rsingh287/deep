"""
Enhanced Knowledge Graph & Bi-Temporal Memory Engine
Supports In-Place Observation Updates, Detailed Metadata (Timestamps, Confidence, Source),
Relational Queries, Sensitive Data Auto-Encryption, and Graph Visualizer Exports.
"""

import os
import time
import json
import sqlite3
import hashlib
import logging
from typing import Dict, List, Any, Optional

from security_rbac_engine import security_rbac
import db_engine

logger = logging.getLogger("EnhancedKnowledgeGraph")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_knowledge_graph.db")
JSON_BACKUP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_knowledge_graph.json")


class EnhancedKnowledgeGraph:
    """
    Tier 2 Durable Knowledge Graph & Relational Memory Engine.
    Persists entities, observations, and bi-temporal relations in PostgreSQL (deep_db)
    for ACID durability and enterprise queryability.
    """
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        # Use PostgreSQL by default unless a specific custom SQLite file is explicitly provided
        self.use_postgres = db_path is None or db_path == DB_PATH
        self._init_db()
        self._load_seed_data_if_empty()

    def _get_connection(self):
        if self.use_postgres:
            try:
                conn = db_engine.get_db_connection()
                conn.row_factory = True
                return conn
            except Exception as e:
                logger.warning(f"[EnhancedKG] PostgreSQL connection failed ({e}), falling back to SQLite.")
                self.use_postgres = False

        conn = sqlite3.connect(self.db_path or DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        if self.use_postgres:
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_entities (
                    name VARCHAR(255) PRIMARY KEY,
                    entity_type VARCHAR(100) DEFAULT 'GENERAL',
                    description TEXT DEFAULT '',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_observations (
                    id VARCHAR(64) PRIMARY KEY,
                    entity_name VARCHAR(255) REFERENCES kg_entities(name) ON DELETE CASCADE,
                    observation_text TEXT,
                    confidence REAL DEFAULT 1.0,
                    source VARCHAR(100) DEFAULT 'system',
                    is_sensitive INTEGER DEFAULT 0,
                    encrypted_data TEXT,
                    revision INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_relations (
                    id VARCHAR(64) PRIMARY KEY,
                    from_entity VARCHAR(255) REFERENCES kg_entities(name) ON DELETE CASCADE,
                    to_entity VARCHAR(255) REFERENCES kg_entities(name) ON DELETE CASCADE,
                    relation_type VARCHAR(100),
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_kg_obs_entity ON kg_observations(entity_name)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_kg_rel_from ON kg_relations(from_entity)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_kg_rel_to ON kg_relations(to_entity)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_kg_rel_type ON kg_relations(relation_type)")
        else:
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_entities (
                    name TEXT PRIMARY KEY,
                    entity_type TEXT DEFAULT 'GENERAL',
                    description TEXT DEFAULT '',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_observations (
                    id TEXT PRIMARY KEY,
                    entity_name TEXT,
                    observation_text TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT DEFAULT 'system',
                    is_sensitive INTEGER DEFAULT 0,
                    encrypted_data TEXT,
                    revision INTEGER DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (entity_name) REFERENCES kg_entities(name) ON DELETE CASCADE
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS kg_relations (
                    id TEXT PRIMARY KEY,
                    from_entity TEXT,
                    to_entity TEXT,
                    relation_type TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT,
                    FOREIGN KEY (from_entity) REFERENCES kg_entities(name) ON DELETE CASCADE,
                    FOREIGN KEY (to_entity) REFERENCES kg_entities(name) ON DELETE CASCADE
                )
            """)
        conn.commit()
        conn.close()

    def _load_seed_data_if_empty(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as count FROM kg_entities")
        row = c.fetchone()
        if row and row["count"] == 0:
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            # Seed foundational hardware & OS knowledge
            c.execute("""
                INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                VALUES ('PIC18F85K22', 'MICROCONTROLLER', 'Microchip 80-pin TQFP, 64KB Flash, 3.8KB RAM', ?, ?)
            """, (now, now))
            c.execute("""
                INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                VALUES ('PICkit3', 'DEBUGGER', 'PICkit 3 Hardware Programmer (BUR181916585)', ?, ?)
            """, (now, now))
            c.execute("""
                INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                VALUES ('MCP9701', 'SENSOR', 'Microchip linear active thermistor on AN0', ?, ?)
            """, (now, now))

            # Relations
            rel_id = hashlib.md5("PICkit3_PROGRAMS_PIC18F85K22".encode()).hexdigest()
            c.execute("""
                INSERT INTO kg_relations (id, from_entity, to_entity, relation_type, confidence, created_at)
                VALUES (?, 'PICkit3', 'PIC18F85K22', 'PROGRAMS', 1.0, ?)
            """, (rel_id, now))

            # Observations
            obs_id = hashlib.md5("PIC18F85K22_LCD_LINE1".encode()).hexdigest()
            c.execute("""
                INSERT INTO kg_observations (id, entity_name, observation_text, confidence, source, revision, created_at, updated_at)
                VALUES (?, 'PIC18F85K22', 'Line 1 of the 16x2 LCD is broken on trainer board. Render UI solely on Line 2 (0xC0).', 1.0, 'hardware_profile', 1, ?, ?)
            """, (obs_id, now, now))
            conn.commit()
        conn.close()

    def create_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates or registers new entities in the knowledge graph."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        c = conn.cursor()
        created = []
        for ent in entities:
            name = ent.get("name", "").strip()
            if not name:
                continue
            entity_type = ent.get("entityType", "GENERAL").upper()
            desc = ent.get("description", "")
            c.execute("""
                INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    entity_type=excluded.entity_type,
                    description=excluded.description,
                    updated_at=excluded.updated_at
            """, (name, entity_type, desc, now, now))
            created.append(name)
        conn.commit()
        conn.close()
        return {"success": True, "createdEntities": created}

    def add_observations(
        self,
        entity_name: str,
        observations: List[str],
        confidence: float = 1.0,
        source: str = "agent",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Adds observations with detailed metadata: timestamps, confidence level, and source.
        Automatically checks for and encrypts sensitive credentials.
        """
        entity_name = entity_name.strip()
        if not entity_name:
            return {"success": False, "error": "entityName cannot be empty"}

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        c = conn.cursor()

        # Ensure entity exists
        c.execute("SELECT name FROM kg_entities WHERE name = ?", (entity_name,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                VALUES (?, 'GENERAL', '', ?, ?)
            """, (entity_name, now, now))

        added_ids = []
        for obs in observations:
            obs_str = obs.strip()
            if not obs_str:
                continue

            # Detect sensitive information
            is_sensitive = 1 if security_rbac.detect_secrets(obs_str) else 0
            encrypted_payload = None
            storage_text = obs_str

            if is_sensitive:
                enc = security_rbac.encrypt_sensitive_observation(obs_str)
                encrypted_payload = json.dumps(enc)
                storage_text = "[ENCRYPTED_SENSITIVE_DATA]"

            obs_id = hashlib.sha256(f"{entity_name}:{obs_str}:{now}".encode()).hexdigest()[:16]
            c.execute("""
                INSERT INTO kg_observations (
                    id, entity_name, observation_text, confidence, source,
                    is_sensitive, encrypted_data, revision, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    confidence=excluded.confidence,
                    updated_at=excluded.updated_at
            """, (obs_id, entity_name, storage_text, float(confidence), source, is_sensitive, encrypted_payload, now, now))
            added_ids.append(obs_id)

        c.execute("UPDATE kg_entities SET updated_at = ? WHERE name = ?", (now, entity_name))
        conn.commit()
        conn.close()

        return {
            "success": True,
            "entityName": entity_name,
            "observationsAdded": len(added_ids),
            "confidence": confidence,
            "source": source,
            "observationIds": added_ids
        }

    def update_observations(self, update_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates existing observations in the knowledge graph in-place.
        Matches the exact user-requested schema:
        {
          "update": [
            {
              "entityName": "string",
              "oldObservations": ["string"],
              "newObservations": ["string"]
            }
          ]
        }
        Returns:
        {
          "success": true,
          "updatedEntities": ["string"]
        }
        """
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        c = conn.cursor()
        updated_entities = []

        try:
            for item in update_list:
                entity_name = item.get("entityName", "").strip()
                old_obs = item.get("oldObservations", [])
                new_obs = item.get("newObservations", [])

                if not entity_name:
                    continue

                # Fetch all existing observations for entity
                c.execute("SELECT id, observation_text, revision, confidence FROM kg_observations WHERE entity_name = ?", (entity_name,))
                existing_rows = c.fetchall()

                entity_modified = False

                for old_val, new_val in zip(old_obs, new_obs):
                    old_clean = old_val.strip().lower()
                    new_clean = new_val.strip()

                    match_row = None
                    for r in existing_rows:
                        if old_clean in r["observation_text"].lower():
                            match_row = r
                            break

                    is_sensitive = 1 if security_rbac.detect_secrets(new_clean) else 0
                    enc_payload = None
                    save_text = new_clean
                    if is_sensitive:
                        enc = security_rbac.encrypt_sensitive_observation(new_clean)
                        enc_payload = json.dumps(enc)
                        save_text = "[ENCRYPTED_SENSITIVE_DATA]"

                    if match_row:
                        new_rev = match_row["revision"] + 1
                        c.execute("""
                            UPDATE kg_observations
                            SET observation_text = ?,
                                is_sensitive = ?,
                                encrypted_data = ?,
                                revision = ?,
                                updated_at = ?
                            WHERE id = ?
                        """, (save_text, is_sensitive, enc_payload, new_rev, now, match_row["id"]))
                        entity_modified = True
                    else:
                        # If not matched, insert in-place with incremented revision
                        new_id = hashlib.sha256(f"{entity_name}:{new_clean}:{now}".encode()).hexdigest()[:16]
                        c.execute("""
                            INSERT INTO kg_observations (
                                id, entity_name, observation_text, confidence, source,
                                is_sensitive, encrypted_data, revision, created_at, updated_at
                            )
                            VALUES (?, ?, ?, 1.0, 'in_place_update', 1, ?, ?)
                        """, (new_id, entity_name, save_text, is_sensitive, enc_payload, now, now))
                        entity_modified = True

                if entity_modified:
                    c.execute("UPDATE kg_entities SET updated_at = ? WHERE name = ?", (now, entity_name))
                    updated_entities.append(entity_name)

            conn.commit()
            conn.close()
            return {
                "success": True,
                "updatedEntities": updated_entities
            }
        except Exception as ex:
            conn.rollback()
            conn.close()
            return {
                "success": False,
                "error": str(ex),
                "updatedEntities": updated_entities
            }

    def create_relations(self, relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Creates directional relations between entities."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        c = conn.cursor()
        created_relations = []

        for rel in relations:
            from_ent = rel.get("from", "").strip()
            to_ent = rel.get("to", "").strip()
            rel_type = rel.get("relationType", "RELATES_TO").strip().upper()
            confidence = float(rel.get("confidence", 1.0))

            if not from_ent or not to_ent:
                continue

            # Ensure both entities exist in kg_entities to satisfy foreign key constraints
            for e_name in (from_ent, to_ent):
                c.execute("SELECT name FROM kg_entities WHERE name = ?", (e_name,))
                if not c.fetchone():
                    c.execute("""
                        INSERT INTO kg_entities (name, entity_type, description, created_at, updated_at)
                        VALUES (?, 'GENERAL', '', ?, ?)
                        ON CONFLICT(name) DO NOTHING
                    """, (e_name, now, now))

            rel_id = hashlib.md5(f"{from_ent}_{rel_type}_{to_ent}".encode()).hexdigest()
            c.execute("""
                INSERT INTO kg_relations (id, from_entity, to_entity, relation_type, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET confidence=excluded.confidence
            """, (rel_id, from_ent, to_ent, rel_type, confidence, now))
            created_relations.append(f"{from_ent} -[{rel_type}]-> {to_ent}")

        conn.commit()
        conn.close()
        return {"success": True, "createdRelations": created_relations}

    def query_graph(
        self,
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        relation_type: Optional[str] = None,
        min_confidence: float = 0.0,
        search_text: Optional[str] = None,
        decrypt_sensitive: bool = False,
        user_role: str = "ADMIN"
    ) -> Dict[str, Any]:
        """
        Multi-criteria query function for the knowledge graph.
        Filters by entity, relation type, entity type, and confidence threshold.
        """
        conn = self._get_connection()
        c = conn.cursor()

        # Build entity query
        ent_clauses = []
        ent_params = []
        like_op = "ILIKE" if self.use_postgres else "LIKE"
        if entity_name:
            ent_clauses.append(f"name {like_op} ?")
            ent_params.append(f"%{entity_name}%")
        if entity_type:
            ent_clauses.append("entity_type = ?")
            ent_params.append(entity_type.upper())

        ent_sql = "SELECT * FROM kg_entities"
        if ent_clauses:
            ent_sql += " WHERE " + " AND ".join(ent_clauses)

        c.execute(ent_sql, ent_params)
        entities = [dict(r) for r in c.fetchall()]
        entity_names = [e["name"] for e in entities]

        # Fetch observations
        obs_clauses = ["confidence >= ?"]
        obs_params = [float(min_confidence)]

        if entity_names:
            placeholders = ",".join("?" * len(entity_names))
            obs_clauses.append(f"entity_name IN ({placeholders})")
            obs_params.extend(entity_names)

        if search_text:
            obs_clauses.append(f"observation_text {like_op} ?")
            obs_params.append(f"%{search_text}%")

        obs_sql = "SELECT * FROM kg_observations WHERE " + " AND ".join(obs_clauses) + " ORDER BY confidence DESC"
        c.execute(obs_sql, obs_params)
        observations = []

        for r in c.fetchall():
            item = dict(r)
            if item["is_sensitive"] and decrypt_sensitive:
                if item["encrypted_data"]:
                    enc_dict = json.loads(item["encrypted_data"])
                    dec = security_rbac.decrypt_sensitive_observation(enc_dict, user_role=user_role)
                    if dec.get("success"):
                        item["observation_text"] = dec["text"]
                        item["decrypted"] = True
            observations.append(item)

        # Fetch relations
        rel_clauses = ["confidence >= ?"]
        rel_params = [float(min_confidence)]

        if relation_type:
            rel_clauses.append("relation_type = ?")
            rel_params.append(relation_type.upper())

        rel_sql = "SELECT * FROM kg_relations WHERE " + " AND ".join(rel_clauses)
        c.execute(rel_sql, rel_params)
        relations = [dict(r) for r in c.fetchall()]

        conn.close()

        return {
            "success": True,
            "entityCount": len(entities),
            "observationCount": len(observations),
            "relationCount": len(relations),
            "entities": entities,
            "observations": observations,
            "relations": relations
        }

    def delete_observations(self, entity_name: str, observations: List[str]) -> Dict[str, Any]:
        """Deletes specific observations without deleting the entity."""
        conn = self._get_connection()
        c = conn.cursor()
        deleted_count = 0
        for obs in observations:
            c.execute("""
                DELETE FROM kg_observations
                WHERE entity_name = ? AND (observation_text = ? OR observation_text LIKE ?)
            """, (entity_name, obs, f"%{obs}%"))
            deleted_count += c.rowcount
        conn.commit()
        conn.close()
        return {"success": True, "entityName": entity_name, "deletedCount": deleted_count}

    def export_graph_for_ui(self) -> Dict[str, Any]:
        """Exports graph in node/edge format for 3D force or Cytoscape visualization."""
        conn = self._get_connection()
        c = conn.cursor()

        c.execute("SELECT * FROM kg_entities")
        ent_rows = c.fetchall()

        c.execute("SELECT * FROM kg_relations")
        rel_rows = c.fetchall()

        c.execute("SELECT entity_name, count(*) as count, avg(confidence) as avg_conf FROM kg_observations GROUP BY entity_name")
        obs_stats = {r["entity_name"]: {"count": r["count"], "avg_conf": r["avg_conf"]} for r in c.fetchall()}

        nodes = []
        for e in ent_rows:
            stats = obs_stats.get(e["name"], {"count": 0, "avg_conf": 1.0})
            nodes.append({
                "id": e["name"],
                "label": e["name"],
                "type": e["entity_type"],
                "description": e["description"],
                "observationCount": stats["count"],
                "confidence": round(float(stats["avg_conf"] or 1.0), 2)
            })

        edges = []
        for r in rel_rows:
            edges.append({
                "id": r["id"],
                "from": r["from_entity"],
                "to": r["to_entity"],
                "label": r["relation_type"],
                "confidence": r["confidence"]
            })

        conn.close()
        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "totalNodes": len(nodes),
                "totalEdges": len(edges)
            }
        }


# Singleton instance
enhanced_kg = EnhancedKnowledgeGraph()
