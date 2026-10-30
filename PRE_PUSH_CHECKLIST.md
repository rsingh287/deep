# 🚀 D.E.E.P. Pre-Push & Release Verification Checklist

> **Authoritative Pre-Flight Verification Guide for GitHub Pushing, Zero-Trust Sanitization, and Master Test Suites**

---

## 🛡️ Step 1: Zero-Trust Pre-Push Security Verification

Before pushing to any remote repository, verify that zero secrets or untracked local databases are committed:

1. **Verify `.env` is NOT tracked in Git**:
   ```powershell
   git status --short | Select-String "\.env"
   ```
   *Expected: Zero output (only `.env.example` should ever be tracked).*

2. **Verify no local database files or vectors are tracked**:
   ```powershell
   git status --short | Select-String "\.(db|sqlite|pt)$"
   ```
   *Expected: Zero output. All local checkpoints, SQLite databases, and vector stores are ignored via `.gitignore`.*

3. **Verify browser profiles and credentials remain untracked**:
   ```powershell
   git status --short | Select-String "pc_app_profile"
   ```
   *Expected: Zero output.*

---

## 🧪 Step 2: Master Test Matrix Verification

Every release must pass all test suites with 100% green status before pushing:

### 1. Sovereign Cockpit Master Diagnostic Audit
```bash
python check_deep.py
```
*Expected Result: `DIAGNOSTIC SUMMARY: 10/10 PASSED | 0 ADVISORIES | 0 CRITICAL`.*

### 2. Phase 3 & 4 v4 Autonomous Evolutionary Test Suite
```bash
python test_phase3_and_4_v4_evolution.py
```
*Expected Result: `Ran 8 tests ... OK` (verifies Genetic Mutator, Differential Shadow, OpenAPI Synthesizer, Self-Healing Sentinel, ORPO, Online EWC++, Counterfactuals, and LoRA Fusion).*

### 3. Phase 3 & 4 v3 Sovereign Cognitive Test Suite
```bash
python test_phase3_and_4_v3_sovereign.py
python test_advanced_phases_3_and_4.py
```
*Expected Result: `Ran 6 tests ... OK` and `Ran 11 tests ... OK` (verifies 15-case FuzzForge, McCabe AST Complexity, SimPO, DPO, and Canary HotSwapper).*

### 4. Tool Forge & Meta-Learning Unit Suites
```bash
python test_phase3_tool_forge.py
python test_phase4_meta_learning.py
```
*Expected Result: `Ran 10 tests ... OK` and `Ran 5 tests ... OK`.*

### 5. Core Hardware & Subsystem Suites
```bash
python test_circuit_ui_and_embedded_mcu.py
python test_user_intents_and_skills.py
python test_pillars_1_and_2.py
python test_pentagi_integration.py
```
*Expected Result: All subtests pass.*

---

## 🌐 Step 3: Live Cockpit Server Verification

Confirm that the live local server is running and responding to health probes:

```powershell
# Probe core UI and v4 API endpoints
python -c "
import urllib.request
for ep in ['/', '/api/forge/tools', '/api/dream/telemetry', '/api/dream/online_ewc']:
    r = urllib.request.urlopen('http://127.0.0.1:5000' + ep, timeout=5)
    print(f'{ep} -> HTTP {r.status}')
"
```
*Expected: All endpoints return `HTTP 200`.*

---

## 📦 Step 4: Staging, Committing & Pushing

Once all checks pass:

```powershell
# 1. Review status
git status

# 2. Stage all modifications
git add -A

# 3. Create semantic commit
git commit -m "feat: upgrade all system documentation and test matrices"

# 4. Push to remote origin
git push origin main
```

---

## 🎯 Final Release Sign-Off
- [x] All 12 Architectural Pillars documented in `ARCHITECTURE.md` and `README.md`.
- [x] Pre-flight secret sanitization verified (`sanitize_secrets.py`).
- [x] Zero-trust AST static analyzer active for SQL queries and dynamic tool code.
- [x] All 7 test suites passing with 100% green status.
- [x] Live Flask daemon running and serving on port 5000.
