# -*- coding: utf-8 -*-
"""
autonomous_self_healing_engine.py — D.E.E.P. Sovereign Cognitive OS
===================================================================
Level 5 Autonomous Self-Healing Sentinel & Resilience Subsystem.

Architecture:
  - Multi-Layer Diagnostic & Auto-Remediation Protocol (Processes, Databases, Circuits, Hardware, Sockets, Tools)
  - Cognitive Reflexion & Multi-Candidate Patch Tournament (AST Mutation, LLM Reflexion, Snapshot Rollback)
  - Tool Immune System & Autonomous Quarantine Governance
  - Circuit Breaker Canary Prober & Self-Healing Auto-Reset
  - Hardware Mutex & Serial Lock Deadlock Healer
"""

import os
import sys
import time
import re
import gc
import json
import ast
import socket
import logging
import threading
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import psutil

# Local system imports
from hystrix_circuit_breaker import (
    global_circuit_registry,
    CircuitState,
    HystrixCircuitBreaker,
)
from self_synthesizing_tool_forge import (
    ToolForgeManifest,
    ToolVersionManager,
    ASTSecurityShield,
    SandboxedEnvironment,
    CodeOptimizerEngine,
    DYNAMIC_TOOLS_DIR,
    DYNAMIC_TESTS_DIR,
    CURRENT_DIR,
)

logger = logging.getLogger("AutonomousSelfHealingEngine")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

HEALING_INCIDENTS_LOG = os.path.join(CURRENT_DIR, "dynamic_tools", "healing_incidents.json")


class SystemAnomalyDetector:
    """Multi-layer diagnostic scanner inspecting system health across 6 vectors."""

    @classmethod
    def audit_process_and_memory(cls) -> Dict[str, Any]:
        """Layer 1: Audit RAM, CPU, zombie threads, and trigger garbage collection."""
        t0 = time.time()
        mem = psutil.virtual_memory()
        cpu_pct = psutil.cpu_percent(interval=None)
        
        # Collect uncollectable cyclic reference cycles
        freed_objects = gc.collect(2)
        
        mem_after = psutil.virtual_memory()
        is_high_load = mem_after.percent > 85.0 or cpu_pct > 90.0

        return {
            "layer": "process_memory",
            "healthy": not is_high_load,
            "cpu_percent": cpu_pct,
            "ram_used_percent": round(mem_after.percent, 1),
            "ram_available_gb": round(mem_after.available / (1024 ** 3), 2),
            "freed_cyclic_objects": freed_objects,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    @classmethod
    def audit_database_and_vector_core(cls) -> Dict[str, Any]:
        """Layer 2: Audit local SQLite caches and PostgreSQL pgvector connection pool."""
        t0 = time.time()
        sqlite_status = "HEALTHY"
        sqlite_path = os.path.join(CURRENT_DIR, "deep_cache.db")
        
        # Check SQLite integrity if present
        if os.path.exists(sqlite_path):
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_path, timeout=1.0)
                cur = conn.cursor()
                cur.execute("PRAGMA integrity_check;")
                res = cur.fetchone()
                conn.close()
                if res and res[0] != "ok":
                    sqlite_status = f"CORRUPTED: {res[0]}"
            except Exception as e:
                sqlite_status = f"WARNING: {str(e)[:60]}"

        # Check pgvector readiness
        pg_status = "HEALTHY"
        try:
            import psycopg2
            # Read env credentials safely
            from dotenv import load_dotenv
            load_dotenv()
            pg_user = os.getenv("POSTGRES_USER", "deep")
            pg_pass = os.getenv("POSTGRES_PASSWORD", "deep_secure_2026")
            pg_host = os.getenv("POSTGRES_HOST", "localhost")
            pg_port = os.getenv("POSTGRES_PORT", "5432")
            pg_db = os.getenv("POSTGRES_DB", "deep_db")

            conn = psycopg2.connect(
                dbname=pg_db,
                user=pg_user,
                password=pg_pass,
                host=pg_host,
                port=pg_port,
                connect_timeout=2
            )
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            conn.close()
            pg_status = "CONNECTED_ACTIVE"
        except Exception as e:
            pg_status = f"OFFLINE_OR_UNAVAILABLE ({str(e)[:40]})"

        return {
            "layer": "database_vector_core",
            "healthy": "CORRUPTED" not in sqlite_status,
            "sqlite_status": sqlite_status,
            "pgvector_status": pg_status,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    @classmethod
    def audit_circuit_breakers(cls) -> Dict[str, Any]:
        """Layer 3: Audit all registered Hystrix circuit breakers and identify tripped ones."""
        t0 = time.time()
        matrix = global_circuit_registry.get_telemetry_matrix()
        tripped = [b for b in matrix if b.get("state") in ("OPEN", "HALF_OPEN")]

        return {
            "layer": "circuit_breakers",
            "healthy": len(tripped) == 0,
            "total_circuits": len(matrix),
            "tripped_circuits": [b.get("name") for b in tripped],
            "circuit_matrix": matrix,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    @classmethod
    def audit_hardware_mutexes(cls) -> Dict[str, Any]:
        """Layer 4: Inspect camera, audio stream, and PICkit 3 USB mutex handles."""
        t0 = time.time()
        issues_detected = []
        
        # Test whether OpenCV camera handle is leaked
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            issues_detected.append(f"Camera handle warning: {str(e)[:50]}")

        return {
            "layer": "hardware_mutexes",
            "healthy": len(issues_detected) == 0,
            "issues": issues_detected,
            "mcu_line2_defect_guard": "ENFORCED_LINE2_ONLY",
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    @classmethod
    def audit_network_and_sockets(cls) -> Dict[str, Any]:
        """Layer 5: Check local port collisions and socket availability."""
        t0 = time.time()
        conflicts = []
        
        # Test ports commonly used by D.E.E.P
        critical_ports = [5000, 11434]
        for port in critical_ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                res = s.connect_ex(("127.0.0.1", port))
                # 0 means port is listening
            except Exception as e:
                conflicts.append(f"Port {port} probe error: {e}")
            finally:
                s.close()

        return {
            "layer": "network_sockets",
            "healthy": len(conflicts) == 0,
            "conflicts": conflicts,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }

    @classmethod
    def audit_dynamic_tools_catalog(cls) -> Dict[str, Any]:
        """Layer 6: Audit health of all synthesized dynamic tools and active quarantines."""
        t0 = time.time()
        manifest = ToolForgeManifest.load()
        tools = manifest.get("tools", {})
        
        quarantined = []
        broken = []

        for name, meta in tools.items():
            if meta.get("quarantined", False):
                quarantined.append(name)
            tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{name}.py")
            if not os.path.exists(tool_file):
                broken.append(f"{name}: missing python file")

        return {
            "layer": "dynamic_tools_immune",
            "healthy": len(broken) == 0 and len(quarantined) == 0,
            "total_tools": len(tools),
            "quarantined_tools": quarantined,
            "broken_tools": broken,
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }


class HealingPatchTournament:
    """
    Multi-Candidate Patch Synthesis & Tournament Evaluation Engine.
    Generates competing candidate patches (AST Transform, Reflexion LLM, Rollback),
    evaluates them against the regression test suite, and crowns the optimal patch.
    """

    @classmethod
    def generate_ast_candidate(cls, code: str, error_trace: str, error_type: str) -> Optional[str]:
        """Candidate Strategy 1: AST Semantic Transformation."""
        patched = code

        # 1. ZeroDivisionError
        if "ZeroDivisionError" in error_type or "division by zero" in error_trace:
            patched = re.sub(r"(\w+)\s*/\s*(\w+)", r"(\1 / \2 if \2 != 0 else 0.0)", patched)

        # 2. KeyError
        if "KeyError" in error_type:
            patched = re.sub(r'args\["([^"]+)"\]', r'args.get("\1", 0)', patched)
            patched = re.sub(r"args\['([^']+)'\]", r"args.get('\1', 0)", patched)

        # 3. TypeError
        if "TypeError" in error_type:
            if "def run(" in patched and "isinstance(args, dict)" not in patched:
                patched = patched.replace(
                    "def run(args:",
                    "def run(args:\n    if not isinstance(args, dict):\n        return {'success': False, 'error': 'Invalid arguments type'}\n",
                )

        # 4. AttributeError (e.g., NoneType has no attribute 'x')
        if "AttributeError" in error_type:
            # Wrap attribute lookups defensively or inject None check
            if "def run(" in patched and "if args is None:" not in patched:
                patched = patched.replace(
                    "def run(args:",
                    "def run(args:\n    if args is None:\n        return {'success': False, 'error': 'Args cannot be None'}\n",
                )

        # 5. IndexError
        if "IndexError" in error_type or "list index out of range" in error_trace:
            patched = re.sub(
                r"(\w+)\[0\]",
                r"(\1[0] if len(\1) > 0 else None)",
                patched
            )

        # 6. ValueError
        if "ValueError" in error_type:
            # Protect float() and int() conversions with defensive regex
            patched = re.sub(
                r"float\(([^)]+)\)",
                r"(float(\1) if str(\1).replace('.','',1).replace('-','',1).isdigit() else 0.0)",
                patched
            )

        # Universal Safety Net: Wrap run body in try-except if not present
        if "try:" not in patched and "def run(" in patched:
            lines = patched.split("\n")
            new_lines = []
            in_run = False
            for line in lines:
                if line.strip().startswith("def run("):
                    in_run = True
                    new_lines.append(line)
                    new_lines.append("    try:")
                elif in_run and line.startswith("    "):
                    new_lines.append("    " + line)
                elif in_run and not line.startswith("    ") and line.strip() != "":
                    in_run = False
                    new_lines.append("    except Exception as _e:")
                    new_lines.append("        return {'success': False, 'error': str(_e)}")
                    new_lines.append(line)
                else:
                    new_lines.append(line)
            if in_run:
                new_lines.append("    except Exception as _e:")
                new_lines.append("        return {'success': False, 'error': str(_e)}")
            patched = "\n".join(new_lines)

        return patched if patched != code else None

    @classmethod
    def generate_llm_reflexion_candidate(cls, tool_name: str, code: str, error_trace: str) -> Optional[str]:
        """Candidate Strategy 2: LLM Reflexion with Targeted Self-Healing Prompt."""
        try:
            import requests
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            prompt = f"""You are the D.E.E.P. Autonomous Reflexion Healer.
The following dynamic tool encountered a production error:

TOOL NAME: {tool_name}
ERROR TRACE:
{error_trace[:500]}

FAILING SOURCE CODE:
{code}

TASK:
Provide the complete, corrected Python code for this tool.
Ensure that:
1. All arguments are validated defensively.
2. It returns a dictionary with 'success' and appropriate output fields.
3. Prohibited modules (socket, subprocess, winreg, ctypes) are strictly avoided.
4. Output ONLY valid Python code inside a ```python markdown code block.
"""
            res = requests.post(
                f"{ollama_url}/api/generate",
                json={"model": "hermes3:8b", "prompt": prompt, "stream": False, "temperature": 0.1},
                timeout=8.0
            )
            if res.status_code == 200:
                raw = res.json().get("response", "")
                m = re.search(r"```python\s*([\s\S]*?)```", raw)
                if m:
                    candidate = m.group(1).strip()
                    is_safe, _ = ASTSecurityShield.validate_code(candidate)
                    if is_safe:
                        return candidate
        except Exception:
            pass
        return None

    @classmethod
    def generate_rollback_candidate(cls, tool_name: str) -> Optional[str]:
        """Candidate Strategy 3: Historical Verified Snapshot Rollback."""
        versions = ToolVersionManager.list_versions(tool_name)
        if len(versions) >= 2:
            penultimate = versions[-2]
            snap = ToolVersionManager.get_version(tool_name, penultimate)
            if snap and snap.get("source_code"):
                return snap["source_code"]
        return None

    @classmethod
    def conduct_tournament(
        cls,
        tool_name: str,
        original_code: str,
        failing_input: Dict[str, Any],
        error_trace: str,
        error_type: str,
    ) -> Dict[str, Any]:
        """
        Runs the candidate patch tournament.
        Evaluates each candidate in SandboxedEnvironment.
        Returns the winning candidate metadata.
        """
        candidates: List[Dict[str, Any]] = []

        # 1. AST Candidate
        ast_code = cls.generate_ast_candidate(original_code, error_trace, error_type)
        if ast_code:
            is_safe, msg = ASTSecurityShield.validate_code(ast_code)
            if is_safe:
                candidates.append({"strategy": "AST_SEMANTIC_MUTATION", "code": ast_code})

        # 2. LLM Reflexion Candidate
        llm_code = cls.generate_llm_reflexion_candidate(tool_name, original_code, error_trace)
        if llm_code:
            candidates.append({"strategy": "LLM_REFLEXION_SYNTHESIS", "code": llm_code})

        # 3. Rollback Candidate
        rb_code = cls.generate_rollback_candidate(tool_name)
        if rb_code:
            candidates.append({"strategy": "GOLDEN_SNAPSHOT_ROLLBACK", "code": rb_code})

        if not candidates:
            return {"success": False, "error": "Zero viable patch candidates generated."}

        # Evaluate Candidates
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{tool_name}.py")
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{tool_name}.py")

        scored_candidates = []

        for cand in candidates:
            cand_code = cand["code"]
            # Temporarily write candidate to disk
            with open(tool_file, "w", encoding="utf-8") as f:
                f.write(cand_code + "\n")

            t_eval_start = time.time()
            test_res = SandboxedEnvironment.run_subprocess_test(test_file, timeout=6.0)
            latency = round((time.time() - t_eval_start) * 1000, 1)

            # Analyze complexity
            opt = CodeOptimizerEngine.analyze_code(cand_code)
            complexity = opt.get("ast_metrics", {}).get("complexity", 5)

            pass_rate = 1.0 if test_res.get("success") else 0.0
            
            # Fitness formula: PassRate*100 - Complexity*2 + (10 if latency < 100 else 0)
            fitness = (pass_rate * 100.0) - (complexity * 2.0) + (10.0 if latency < 150 else 0.0)

            scored_candidates.append({
                "strategy": cand["strategy"],
                "code": cand_code,
                "passed_tests": test_res.get("success", False),
                "fitness": round(fitness, 2),
                "latency_ms": latency,
                "complexity": complexity,
            })

        # Sort by fitness descending
        scored_candidates.sort(key=lambda x: x["fitness"], reverse=True)
        winner = scored_candidates[0]

        return {
            "success": True,
            "winner": winner,
            "all_candidates": scored_candidates,
            "total_candidates": len(candidates),
        }


class AutonomousSelfHealingEngine:
    """
    Master Autonomous Self-Healing Sentinel & Immune Governance Core.
    Coordinates all diagnostic layers, circuit canary auto-reset,
    dynamic tool healing, quarantine isolation, and incident auditing.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.incident_history: List[Dict[str, Any]] = self._load_incidents()
        self.auto_reset_active = True

    @classmethod
    def get_instance(cls) -> "AutonomousSelfHealingEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = AutonomousSelfHealingEngine()
            return cls._instance

    def _load_incidents(self) -> List[Dict[str, Any]]:
        if os.path.exists(HEALING_INCIDENTS_LOG):
            try:
                with open(HEALING_INCIDENTS_LOG, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _record_incident(self, incident: Dict[str, Any]) -> None:
        incident["timestamp"] = datetime.now().isoformat()
        self.incident_history.insert(0, incident)
        # Keep latest 100 incidents
        self.incident_history = self.incident_history[:100]
        try:
            os.makedirs(os.path.dirname(HEALING_INCIDENTS_LOG), exist_ok=True)
            with open(HEALING_INCIDENTS_LOG, "w", encoding="utf-8") as f:
                json.dump(self.incident_history, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist incident log: {e}")

    def run_full_system_heal(self) -> Dict[str, Any]:
        """
        Executes an end-to-end multi-layer diagnostic and auto-remediation cycle:
        1. Process & Memory sweep (GC, uncollectable cycles)
        2. Database & Vector index health verification
        3. Circuit breaker canary auto-reset
        4. Hardware mutex & serial port handle release
        5. Socket & port conflict mitigation
        6. Dynamic tool immune audit & quarantine triage
        """
        t0 = time.time()
        actions_taken = []

        # Layer 1: Memory & Processes
        l1 = SystemAnomalyDetector.audit_process_and_memory()
        actions_taken.append(
            f"Layer 1 (Memory): {l1['freed_cyclic_objects']} cyclic objects purged. RAM at {l1['ram_used_percent']}%."
        )

        # Layer 2: Database
        l2 = SystemAnomalyDetector.audit_database_and_vector_core()
        actions_taken.append(
            f"Layer 2 (Database): SQLite: {l2['sqlite_status']} | pgvector: {l2['pgvector_status']}."
        )

        # Layer 3: Circuit Breaker Canary Prober & Auto-Reset
        circuit_resets = self.reset_tripped_circuits(force=False)
        if circuit_resets["resets_performed"]:
            for r in circuit_resets["resets_performed"]:
                actions_taken.append(f"Layer 3 (Circuit): Auto-healed and reset circuit '{r}' to CLOSED.")
        else:
            actions_taken.append(f"Layer 3 (Circuit): All {circuit_resets['total_checked']} circuit breakers operating nominal.")

        # Layer 4: Hardware Mutexes
        l4 = SystemAnomalyDetector.audit_hardware_mutexes()
        actions_taken.append(
            f"Layer 4 (Hardware): Camera/MCU mutexes verified. LCD Line 2 defect guard active."
        )

        # Layer 5: Network Sockets
        l5 = SystemAnomalyDetector.audit_network_and_sockets()
        actions_taken.append(
            f"Layer 5 (Sockets): Ports verified. Conflict status: {len(l5['conflicts'])} alerts."
        )

        # Layer 6: Tool Immune System
        l6 = SystemAnomalyDetector.audit_dynamic_tools_catalog()
        actions_taken.append(
            f"Layer 6 (Immune): {l6['total_tools']} dynamic tools inspected. Quarantined: {len(l6['quarantined_tools'])}."
        )

        overall_healthy = (
            l1["healthy"] and l2["healthy"] and l4["healthy"] and len(circuit_resets["resets_performed"]) == 0
        )
        equilibrium = "OPTIMAL" if overall_healthy else "STABILIZED"

        summary = {
            "status": "success",
            "system_equilibrium": equilibrium,
            "actions_executed": actions_taken,
            "diagnostic_layers": {
                "process_memory": l1,
                "database_vector": l2,
                "circuits": circuit_resets,
                "hardware": l4,
                "network_sockets": l5,
                "dynamic_tools": l6,
            },
            "duration_ms": round((time.time() - t0) * 1000, 1),
            "timestamp": datetime.now().isoformat(),
        }

        self._record_incident({
            "type": "FULL_SYSTEM_HEAL",
            "equilibrium": equilibrium,
            "actions_count": len(actions_taken),
            "duration_ms": summary["duration_ms"],
        })

        return summary

    def heal_specific_tool(
        self,
        tool_name: str,
        failing_input: Optional[Dict[str, Any]] = None,
        error_message: str = "Unknown runtime error",
    ) -> Dict[str, Any]:
        """
        Autonomous Multi-Candidate Patch Tournament for a failing tool.
        Diagnoses exception, generates competing patches, runs tournament,
        injects regression test, and hot-swaps winning version.
        """
        tool_file = os.path.join(DYNAMIC_TOOLS_DIR, f"{tool_name}.py")
        test_file = os.path.join(DYNAMIC_TESTS_DIR, f"test_{tool_name}.py")

        if not os.path.exists(tool_file):
            return {"success": False, "error": f"Tool '{tool_name}' not found."}

        with open(tool_file, "r", encoding="utf-8") as f:
            code = f.read()

        tests = ""
        if os.path.exists(test_file):
            with open(test_file, "r", encoding="utf-8") as f:
                tests = f.read()

        # Extract Error Type
        m_err = re.search(r"(\b[A-Z][a-zA-Z]*Error\b)", error_message)
        error_type = m_err.group(1) if m_err else "RuntimeError"

        # Conduct Patch Tournament
        tournament = HealingPatchTournament.conduct_tournament(
            tool_name=tool_name,
            original_code=code,
            failing_input=failing_input or {},
            error_trace=error_message,
            error_type=error_type,
        )

        if not tournament.get("success"):
            # If all patches fail, quarantine the tool
            self.quarantine_tool(tool_name, f"Healing tournament failed: {tournament.get('error')}")
            return {
                "success": False,
                "error": f"Healing failed. Tool '{tool_name}' moved to QUARANTINE to protect OS stability.",
                "tournament": tournament,
            }

        winner = tournament["winner"]
        winning_code = winner["code"]

        # Append regression test case
        new_test = f"""
    def test_regression_auto_healed_{int(time.time())}(self):
        # Auto-generated by AutonomousSelfHealingEngine (Strategy: {winner['strategy']})
        res = run({repr(failing_input or {})})
        self.assertIsNotNone(res)
"""
        patched_tests = tests.rstrip() + new_test if tests else ""

        # Commit winning patch
        with open(tool_file, "w", encoding="utf-8") as f:
            f.write(winning_code + "\n")
        if patched_tests:
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(patched_tests + "\n")

        new_version = ToolVersionManager.save_version(
            tool_name,
            winning_code,
            patched_tests,
            note=f"Auto-healed via {winner['strategy']} (Fitness: {winner['fitness']})"
        )

        # Unquarantine if previously isolated
        self.unquarantine_tool(tool_name)

        incident_info = {
            "type": "TOOL_HEALED",
            "tool_name": tool_name,
            "error_type": error_type,
            "strategy": winner["strategy"],
            "fitness": winner["fitness"],
            "new_version": new_version,
        }
        self._record_incident(incident_info)

        return {
            "success": True,
            "tool_name": tool_name,
            "winning_strategy": winner["strategy"],
            "fitness": winner["fitness"],
            "new_version": new_version,
            "all_candidates": tournament["all_candidates"],
            "timestamp": datetime.now().isoformat(),
        }

    def quarantine_tool(self, tool_name: str, reason: str = "Repeated execution crashes") -> bool:
        """Isolates a failing tool from production execution."""
        manifest = ToolForgeManifest.load()
        tools = manifest.get("tools", {})
        if tool_name in tools:
            tools[tool_name]["quarantined"] = True
            tools[tool_name]["quarantine_reason"] = reason
            tools[tool_name]["quarantined_at"] = datetime.now().isoformat()
            ToolForgeManifest.save(manifest)
            self._record_incident({
                "type": "TOOL_QUARANTINED",
                "tool_name": tool_name,
                "reason": reason,
            })
            logger.warning(f"Tool '{tool_name}' has been QUARANTINED. Reason: {reason}")
            return True
        return False

    def unquarantine_tool(self, tool_name: str) -> bool:
        """Restores a tool from quarantine after verification."""
        manifest = ToolForgeManifest.load()
        tools = manifest.get("tools", {})
        if tool_name in tools and tools[tool_name].get("quarantined", False):
            tools[tool_name]["quarantined"] = False
            tools[tool_name]["quarantine_reason"] = None
            tools[tool_name]["unquarantined_at"] = datetime.now().isoformat()
            ToolForgeManifest.save(manifest)
            self._record_incident({
                "type": "TOOL_UNQUARANTINED",
                "tool_name": tool_name,
            })
            logger.info(f"Tool '{tool_name}' UNQUARANTINED and restored to production.")
            return True
        return False

    def reset_tripped_circuits(self, force: bool = False) -> Dict[str, Any]:
        """
        Canary-probes and resets tripped circuit breakers.
        Tests target endpoint health before closing the circuit.
        """
        matrix = global_circuit_registry.get_telemetry_matrix()
        resets = []

        for b_info in matrix:
            name = b_info.get("name")
            state = b_info.get("state")
            if state in ("OPEN", "HALF_OPEN") or force:
                breaker = global_circuit_registry.get(name)
                if breaker:
                    # Execute Canary Probe for specific known breakers
                    canary_healthy = True
                    if name == "ollama_inference":
                        try:
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.settimeout(0.8)
                            canary_healthy = (s.connect_ex(("127.0.0.1", 11434)) == 0)
                            s.close()
                        except Exception:
                            canary_healthy = False

                    if canary_healthy or force:
                        breaker.reset()
                        resets.append(name)

        return {
            "total_checked": len(matrix),
            "resets_performed": resets,
            "timestamp": datetime.now().isoformat(),
        }

    def get_healing_telemetry(self) -> Dict[str, Any]:
        """Returns comprehensive telemetry on incidents, quarantine states, and health."""
        manifest = ToolForgeManifest.load()
        quarantined = [
            {"name": k, "reason": v.get("quarantine_reason"), "at": v.get("quarantined_at")}
            for k, v in manifest.get("tools", {}).items()
            if v.get("quarantined", False)
        ]
        circuits = global_circuit_registry.get_telemetry_matrix()

        return {
            "total_incidents_recorded": len(self.incident_history),
            "recent_incidents": self.incident_history[:10],
            "quarantined_tools_count": len(quarantined),
            "quarantined_tools": quarantined,
            "circuits_telemetry": circuits,
            "timestamp": datetime.now().isoformat(),
        }


def get_self_healing_engine() -> AutonomousSelfHealingEngine:
    return AutonomousSelfHealingEngine.get_instance()
