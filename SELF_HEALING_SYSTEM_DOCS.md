# 🩺 D.E.E.P. Autonomous Self-Healing & Resilience Architecture

> **Authoritative Specification for Multi-Turn Reflexion, Runtime Exception Interception, Hystrix Circuit Breakers, and Zero-Downtime Rollback**

---

## 📖 Executive Summary

The **D.E.E.P Sovereign Cognitive Workstation** implements an active, multi-layered self-healing architecture designed to eliminate runtime crashes, automatically recover from syntax or algorithmic bugs in synthesized tools, prevent model performance regression, and maintain high service availability without human intervention.

```
                     ┌──────────────────────────────────────────────┐
                     │          Autonomous System Event             │
                     └──────────────────────┬───────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               │                            │                            │
      ┌────────▼─────────┐         ┌────────▼─────────┐         ┌────────▼─────────┐
      │  Tool Synthesis  │         │  Live Execution  │         │ Model Promotion  │
      │   Test Failure   │         │    Exception     │         │ Degradation Drift│
      └────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
               │                            │                            │
      ┌────────▼─────────┐         ┌────────▼─────────┐         ┌────────▼─────────┐
      │ Reflexion Engine │         │ Self-Healing     │         │ Canary Benchmark │
      │ 3-Turn Diagnostic│         │ Sentinel Auto-Fix│         │ 1-Click Rollback │
      └──────────────────┘         └──────────────────┘         └──────────────────┘
```

---

## 1. Multi-Turn Reflexion Engine (`ReflexionEngine`)
*Located in [`self_synthesizing_tool_forge.py`](self_synthesizing_tool_forge.py)*

When a newly synthesized tool fails its automated test suite, D.E.E.P does not abandon the task or request user intervention. Instead, the [`ReflexionEngine`](self_synthesizing_tool_forge.py) executes an iterative 3-turn self-healing loop:

1. **Diagnostic Traceback Extraction**:
   - Parses stderr output for exact exception types (`AssertionError`, `KeyError`, `TypeError`, `ZeroDivisionError`).
   - Identifies the precise file and line number of the failure (`test_<tool>.py:<line>` or `<tool>.py:<line>`).
   - Generates a structured diagnostic hint explaining the discrepancy.
2. **Reflective Prompt Formulation**:
   - Formulates a targeted prompt containing the failing code, unit test expectation, exact traceback, and diagnostic hint.
3. **Iterative Code Repair & Re-verification**:
   - The local LLM generates a targeted patch.
   - The patch is re-evaluated by the [`ASTSecurityShield`](self_synthesizing_tool_forge.py).
   - If safe, the test suite is executed in the isolated subprocess sandbox. The loop repeats up to 3 turns until tests pass.

---

## 2. Production Runtime Self-Healing Sentinel (`ToolSelfHealingSentinel`)
*Located in [`self_synthesizing_tool_forge.py`](self_synthesizing_tool_forge.py)*

If an already-verified synthesized tool encounters an unexpected runtime exception in production:

1. **Exception Interception**:
   - The exception is captured along with the offending input arguments and stack trace.
2. **Automated Root Cause Diagnosis**:
   - [`ReflexionEngine.diagnose_failure()`](self_synthesizing_tool_forge.py) determines whether the failure stems from missing dictionary keys (`KeyError`), division by zero (`ZeroDivisionError`), or argument type mismatches (`TypeError`).
3. **Targeted AST Patching**:
   - Converts direct dictionary index lookups (`args["key"]`) to safe `.get("key", default)`.
   - Injects zero-division guards: `(a / b if b != 0 else 0.0)`.
   - Injects short-circuit input validation guards at the function entrypoint.
4. **Regression Unit Test Generation**:
   - Automatically writes a new unit test case reproducing the failing input (`test_regression_healed_<timestamp>`).
5. **Atomic Version Bump & Hot-Swap**:
   - Verifies the patched code against the entire existing test suite plus the new regression test.
   - Saves a new immutable version snapshot in `dynamic_tools/versions/<tool>/v<N>.json`.
   - Hot-swaps the patched module into the running Python runtime without restarting the workstation.

---

## 3. Hystrix Fail-Fast Circuit Breakers (`HystrixCircuitBreaker`)
*Located in [`hystrix_circuit_breaker.py`](hystrix_circuit_breaker.py)*

To protect the Cockpit UI and voice co-pilot loops from blocking or hanging during external API latency or hardware disconnects, critical operations are wrapped in stateful circuit breakers:

| Breaker Name | Monitored Target | Failure Threshold | Reset Timeout |
| :--- | :--- | :--- | :--- |
| `ollama_inference` | Local Ollama LLM HTTP API | 3 consecutive failures | 15.0 seconds |
| `iot_smart_home` | Kasa Smart Plugs / LAN devices | 2 consecutive timeouts | 10.0 seconds |
| `screen_vision` | Camera & Screen Capture Handles | 3 frame acquisition errors | 10.0 seconds |
| `mcu_flasher` | PICkit 3 USB Hardware Interface | 2 USB communication errors | 30.0 seconds |

### Circuit State Transitions
- **`CLOSED`**: Normal operational state. Calls pass through; latency metrics are tracked.
- **`OPEN`**: Tripped when error or timeout threshold is breached. Subsequent calls fail fast immediately (sub-millisecond latency) returning cached fallbacks or error codes without blocking the thread.
- **`HALF-OPEN`**: After the reset timeout expires, a single trial request is permitted. If successful, the breaker resets to `CLOSED`; if it fails, it returns to `OPEN`.

---

## 4. Shadow Canary Benchmarking & Hot-Swap Failover (`CanaryHotSwapper`)
*Located in [`nightly_meta_learner.py`](nightly_meta_learner.py)*

Before newly trained LoRA weights or candidate models are promoted to production in Ollama:

1. **Shadow Probe Battery**:
   - The candidate model is probed against critical golden prompts:
     - **AST Guardrail Defense**: Attempting `DROP TABLE users;` must trigger `SECURITY_VIOLATION`.
     - **PIC18F85K22 LCD Defect Compliance**: Requesting LCD Line 1 must warn that Line 1 is defective and render solely on Line 2.
     - **Local Music Routing**: Querying a song must match the local library and avoid opening unauthorized browser tabs.
2. **Automated Promotion or Abort**:
   - If the candidate achieves a score $\ge 80/100$, it is compiled into `Modelfile.deep_sovereign` and deployed to `deep-sovereign:latest`.
   - If the score falls below threshold, promotion is automatically aborted, the existing stable weights are retained, and the failure is logged to telemetry.

---

## 5. Immutable Versioning & 1-Click Rollback (`ToolVersionManager`)
*Located in [`self_synthesizing_tool_forge.py`](self_synthesizing_tool_forge.py)*

Every tool mutation, optimization, and synthesis is immutably archived in:
`dynamic_tools/versions/<tool_name>/v<N>.json`

- **Integer-Sorted History**: Historical snapshots are indexed numerically (`v1`, `v2`, ... `v20`), ensuring deterministic ordering.
- **Instant Rollback**: If a tool behaves unexpectedly, invoking [`/api/forge/rollback`](routes/tool_forge_bp.py) or clicking **Rollback** in the Cockpit UI restores the penultimate version atomically and updates the active manifest in $< 5	ext{ms}$.

---

## 6. Lifelong Continual Learning Regularization (`OnlineFisherConsolidator`)
*Located in [`nightly_meta_learner.py`](nightly_meta_learner.py)*

To eliminate **catastrophic forgetting** across multi-night meta-learning runs:

- Computes diagonal Fisher Information Matrix $F_i$ on canonical anchor tasks.
- Updates a running Fisher matrix with momentum decay:
  $$F_{\text{running}}^{(t)} = \gamma F_{\text{running}}^{(t-1)} + (1 - \gamma) F_{\text{new}} \quad (\gamma = 0.90)$$
- Applies a quadratic penalty during LoRA optimization:
  $$\mathcal{L}_{\text{EWC}} = \frac{\lambda_{\text{EWC}}}{2} \sum_i F_i (\theta_i - \theta_i^*)^2$$
- Guarantees that adapting to new user preferences never degrades hardware safety rules, AST guardrails, or voice brevity.
