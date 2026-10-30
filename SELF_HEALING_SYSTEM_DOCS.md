# 🩺 D.E.E.P. Autonomous Self-Healing & Resilience Architecture (Level 5)

> **Authoritative Specification for Full-Spectrum Multi-Layer Diagnostics, Candidate Patch Tournaments, Tool Immune Quarantine, Circuit Canary Auto-Reset, and Zero-Downtime Hot-Swapping**

---

## 📖 Executive Summary

The **D.E.E.P Sovereign Cognitive Workstation** implements an active, multi-vector **Level 5 Autonomous Self-Healing Sentinel & Immune Governance Subsystem** (`autonomous_self_healing_engine.py`). Engineered for air-gapped bare-metal environments, the system autonomously identifies anomalies across 6 system layers, executes multi-candidate patch tournaments, quarantines unstable tools to prevent cascading failures, and canary-probes tripped circuit breakers without human intervention.

```
                      ┌──────────────────────────────────────────────┐
                      │          Autonomous System Event             │
                      └──────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
      │                  │                   │                   │                  │
┌─────▼─────┐      ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐      ┌─────▼─────┐
│ Layer 1-2 │      │  Layer 3  │       │  Layer 4  │       │  Layer 5  │      │  Layer 6  │
│ Processes │      │ Circuits  │       │ Hardware  │       │  Sockets  │      │  Immune   │
│ & Database│      │ Canary    │       │ Mutexes   │       │ Conflicts │      │ Quarantine│
└─────┬─────┘      └─────┬─────┘       └─────┬─────┘       └─────┬─────┘      └─────┬─────┘
      │                  │                   │                   │                  │
      └──────────────────┴───────────────────┼───────────────────┴──────────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │ HealingPatchTournament        │
                             │  1. AST Semantic Mutation     │
                             │  2. LLM Reflexion Synthesis   │
                             │  3. Golden Snapshot Rollback  │
                             └───────────────┬───────────────┘
                                             │ Highest Fitness
                             ┌───────────────▼───────────────┐
                             │ Sandboxed Invariant Verifier  │
                             │  + Timestamped Regression Test│
                             └───────────────┬───────────────┘
                                             │
                             ┌───────────────▼───────────────┐
                             │ Atomic Version Hot-Swap (vN)  │
                             └───────────────────────────────┘
```

---

## 1. The 6-Layer Diagnostic & Auto-Remediation Matrix (`SystemAnomalyDetector`)

The sentinel monitors and repairs 6 core architectural layers during every healing cycle:

| Layer | Monitored Vectors | Diagnostic Metrics | Autonomous Remediation Protocol |
| :---: | :--- | :--- | :--- |
| **Layer 1** | **Processes & Memory** | RAM %, CPU %, cyclic object leaks, zombie tasks | Executes `gc.collect(2)` purging uncollectable cyclic reference cycles. Reclaims cache memory when RAM $> 80\%$. |
| **Layer 2** | **Storage & Database** | SQLite cache integrity, PostgreSQL `deep_db` pool | Runs `PRAGMA integrity_check` on SQLite. Tests pgvector pool readiness with `SELECT 1`; auto-recycles hung pool connections. |
| **Layer 3** | **Circuit Breakers** | Hystrix breaker states (`CLOSED`, `OPEN`, `HALF_OPEN`) | Detects tripped circuits and executes non-blocking canary health probes. Resets recovered circuits to `CLOSED` automatically. |
| **Layer 4** | **Hardware Mutexes** | Camera handles, audio streams, PICkit 3 USB mutex | Forcibly releases leaked `cv2.VideoCapture` handles, releases audio streams, and guarantees PIC18F85K22 LCD Line 2 defect guard enforcement. |
| **Layer 5** | **Network & Sockets** | Local port collisions (`[WinError 10048]`), listener state | Identifies port collisions (e.g. honeypots on 2222/33060), safely releases dead socket descriptors, and re-allocates alternative ports. |
| **Layer 6** | **Tool Immune System** | Dynamic tools catalog, crash rates, quarantine state | Triages tools with repeated crashes ($\ge 3$), isolates them into `QUARANTINED` status, and runs the Multi-Candidate Patch Tournament. |

---

## 2. Multi-Candidate Patch Tournament (`HealingPatchTournament`)

When a synthesized tool encounters an unhandled runtime error, D.E.E.P does not rely on a single fragile fix. Instead, it generates competing candidate patches across three distinct strategies and runs an automated **Patch Tournament**:

### Candidate Strategies
1. **Strategy 1: AST Semantic Mutation (`AST_SEMANTIC_MUTATION`)**:
   - Parses the code into Python AST nodes.
   - **`ZeroDivisionError`**: Injects denominator safety guards: `(a / b if b != 0 else 0.0)`.
   - **`KeyError`**: Converts dictionary bracket access `args["k"]` to `args.get("k", 0)`.
   - **`TypeError`**: Injects input type checking: `if not isinstance(args, dict): return {'success': False}`.
   - **`AttributeError`**: Injects `NoneType` safety checks before attribute access.
   - **`IndexError`**: Guards list index lookups with sequence length validation.
   - **`ValueError`**: Protects numeric casts with defensive validation regex.
   - **Universal Safety Net**: Wraps function body in a defensive `try...except Exception as _e:` fallback block.
2. **Strategy 2: LLM Reflexion Synthesis (`LLM_REFLEXION_SYNTHESIS`)**:
   - Formulates a targeted prompt with the failing code, exact traceback, and Reflexion diagnosis.
   - Calls local Ollama LLM (`hermes3:8b`) with high temperature penalty to synthesize an alternative algorithmic patch.
   - Validates generated code against [`ASTSecurityShield`](self_synthesizing_tool_forge.py).
3. **Strategy 3: Golden Snapshot Rollback (`GOLDEN_SNAPSHOT_ROLLBACK`)**:
   - Retrieves the most recent historically verified version snapshot from `dynamic_tools/versions/<tool>/`.

### Candidate Fitness Scoring & Crown
All candidates are evaluated in the [`SandboxedEnvironment`](self_synthesizing_tool_forge.py) against the existing test suite + dynamic regression test:

$$\text{Fitness} = (\text{PassRate} \times 100.0) - (\text{Complexity} \times 2.0) + (\text{SpeedupBonus})$$

The candidate with the highest fitness score is crowned the winner, saved as a new version snapshot, and hot-swapped into production.

---

## 3. Tool Immune System & Quarantine Governance

To prevent unstable or corrupted tools from degrading Cockpit UI response times or hanging agent execution:

- **Automatic Quarantine**: If a tool crashes repeatedly ($\ge 3$ consecutive failures) or fails all tournament candidates, the sentinel immediately sets `"quarantined": true` in `dynamic_tools/manifest.json`.
- **Graceful Divergence**: Quarantined tools are intercepted at the gateway; any attempt to invoke them returns a safe status code (`TOOL_QUARANTINED`) rather than raising unhandled exceptions.
- **Operator Notification**: Quarantined tools are prominently surfaced in the **Cockpit Self-Healing Sentinel Studio**.
- **1-Click Auto-Heal & Unquarantine**: Clicking **"Repair & Restore"** triggers an emergency patch tournament and, upon successful test passage, restores the tool to active production (`"quarantined": false`).

---

## 4. Circuit Breaker Canary Auto-Reset Protocol

The Sentinel inspects all registered Hystrix circuit breakers (`global_circuit_registry`):

1. **Detection**: Any breaker in `OPEN` or `HALF_OPEN` state is flagged for canary validation.
2. **Canary Probe**:
   - For `ollama_inference`: Establishes a lightweight socket handshake to `127.0.0.1:11434` with sub-800ms timeout.
   - For `screen_vision`: Attempts webcam handle acquisition and deterministic release.
   - For `iot_smart_home`: Pings the target LAN IP address.
3. **State Transition**: If the canary probe confirms the underlying resource is healthy, `breaker.reset()` transitions the breaker directly to `CLOSED`, restoring full operational throughput.

---

## 5. REST API Specification

The Self-Healing Sentinel exposes comprehensive REST endpoints via `routes/self_heal_bp.py`:

| Method | Path | Request Body | Description |
| :---: | :--- | :--- | :--- |
| `POST` | `/api/heal/system` | None | Triggers full-spectrum 6-layer autonomous self-healing sweep. |
| `POST` | `/api/heal/tool` | `{"tool_name": "...", "failing_input": {...}, "error_message": "..."}` | Runs multi-candidate patch tournament to heal a specific tool. |
| `GET` | `/api/heal/telemetry` | None | Returns incident history, active quarantines, and circuit states. |
| `POST` | `/api/heal/reset_circuits` | `{"force": false}` | Canary-probes and resets tripped circuit breakers. |
| `POST` | `/api/heal/quarantine` | `{"tool_name": "...", "reason": "..."}` | Manually isolates an unstable tool from execution. |
| `POST` | `/api/heal/unquarantine` | `{"tool_name": "..."}` | Restores a repaired tool to production. |

---

## 6. Verification & Test Suite Runbook

The complete Level 5 Self-Healing Sentinel is validated by [`test_advanced_self_healing_v5.py`](test_advanced_self_healing_v5.py):

```bash
# Execute Level 5 Autonomous Self-Healing Verification Suite
python test_advanced_self_healing_v5.py
```

*Expected Result: `Ran 8 tests ... OK` in < 20s.*
- `test_01_six_layer_diagnostic_matrix`: Verifies all 6 diagnostic layers.
- `test_02_ast_semantic_mutation_error_classes`: Verifies AST handlers across 6 Python error classes.
- `test_03_full_system_healing_sweep`: Verifies system equilibrium status (`OPTIMAL`).
- `test_04_tool_immune_quarantine_lifecycle`: Verifies Quarantine $\rightarrow$ Isolation $\rightarrow$ Unquarantine.
- `test_05_circuit_breaker_canary_auto_reset`: Verifies canary-probed circuit recovery.
- `test_06_patch_tournament_healing_execution`: Verifies tournament evaluation and fitness scoring.
- `test_07_rest_api_self_heal_endpoints`: Verifies all REST endpoints return `HTTP 200`.
- `test_08_natural_language_self_healing_intent`: Verifies conversational `"self heal"` voice commands.
