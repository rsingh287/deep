# 🛡️ Security Policy & Zero-Trust Governance

## Zero-Trust Architecture & Safeguards

The **D.E.E.P (Dynamic Executive Edge Platform)** adheres to strict zero-trust security principles designed to prevent credential exfiltration, destructive hardware operations, unauthorized code execution, and unvalidated model drift.

---

### Core Security Guarantees & Defense-in-Depth

#### 1. Pre-Flight Secret Sanitization & PII Scrubbing
- All user prompts, agent thoughts, terminal outputs, and database records pass through AST-level secret scanners (`sanitize_secrets.py`) and PII extractors (`pii_ner_extractor_engine.py`).
- API keys, private tokens, passwords, and database connection strings are strictly redacted (`[REDACTED_SECRET]`) prior to logging, display in the UI, or storage in database tables.

#### 2. AST-Enforced Safe Database Execution
- Every AI-generated SQL query is parsed into a Python Abstract Syntax Tree (`enterprise_ai_guardrails.py`) before reaching the PostgreSQL database.
- Destructive DDL and DML operations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) are blocked unconditionally and raise `SECURITY_VIOLATION`.
- Telemetry and analytical queries are strictly read-only and enforce an automated `LIMIT 100` ceiling.

#### 3. Zero-Trust AST Security Shield for Synthesized Tools
- When the **Self-Synthesizing Tool Forge** creates or mutates a dynamic Python tool, the code is evaluated against [`ASTSecurityShield`](self_synthesizing_tool_forge.py):
  - **Banned Builtins**: `eval`, `exec`, `compile`, `__import__`, `globals`, `locals`, `vars`.
  - **Banned Modules**: `winreg`, `ctypes`, `msvcrt`, `win32api`, `subprocess`, `socket`, `pty`.
  - **Banned OS Mutations**: `os.system`, `os.popen`, `os.spawn`, `os.fork`.
  - **Introspection Sandbox Escape Defense**: Access to `__subclasses__`, `__bases__`, `__globals__`, and `__code__` is strictly intercepted and rejected.

#### 4. Secret-Sanitized Subprocess Execution Sandbox
- Unit tests and execution verification runs for dynamically synthesized tools execute inside isolated subprocesses managed by [`SandboxedEnvironment`](self_synthesizing_tool_forge.py).
- Environment variables containing sensitive credentials (`TOKEN`, `KEY`, `SECRET`, `PASS`, `AUTH`, `DATABASE_URL`) are aggressively stripped before child processes launch.

#### 5. Differential Shadow Verification & Regression Defense
- Before any synthesized tool mutation is promoted to production, [`DifferentialShadowRunner`](self_synthesizing_tool_forge.py) executes both versions side-by-side on historical test vectors in isolated sandboxes.
- A semantic divergence rate of $0.0\%$ is strictly enforced to guarantee zero regression drift.

#### 6. Adversarial Counterfactual Sleep Hardening
- During nightly machine dreaming, [`CounterfactualDreamSimulator`](nightly_meta_learner.py) synthesizes adversarial failure scenarios (prompt injection bypass attempts, SQL DDL injections, unauthorized socket executions) and trains the local model via ORPO/SimPO to resist adversarial attacks.

#### 7. Human-in-the-Loop (HITL) Gate for Destructive Actions
- Permanent file deletions, closing active user application windows, killing external processes, or system reboots require explicit verbal confirmation or an authenticated UI confirmation modal.

#### 8. Hardware Resource Mutex Locks
- Physical hardware handles (Microchip PICkit 3 programmer, OpenCV video capture, audio streams) are acquired with deterministic mutex locks and released inside `finally` blocks to prevent bus contention or device busy lockouts.

#### 9. Network Boundary & Local Scoping
- The PentAGI DAST testing bridge is hard-locked to local RFC 1918 private subnets (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `localhost`).
- Scanning or probing external internet IP addresses is prohibited and blocked at the route handler level.

---

### Supported Versions

| Version | Supported          | Release Tier |
| ------- | ------------------ | ------------ |
| 4.0.x   | :white_check_mark: | Active (v4 Sovereign Evolution) |
| 3.0.x   | :white_check_mark: | Maintenance (v3 Cognitive Foundry) |
| 2.0.x   | :white_check_mark: | Maintenance |
| < 2.0   | :x:                | Deprecated |

---

### Reporting a Vulnerability

If you discover a potential security vulnerability within this project, please report it responsibly:

1. **Do NOT open a public GitHub issue** disclosing sensitive details, reproduction steps, or exploit proofs.
2. Email the maintainer or submit a private security advisory through GitHub:
   - Navigate to the **Security** tab of this repository.
   - Click **Report a vulnerability**.
3. Include detailed reproduction steps, system environment, and observed versus expected behavior.
4. Security advisories are acknowledged within 24 to 48 hours, and patches are prioritized immediately.
