# 🤝 Contributing to D.E.E.P. Sovereign Cognitive OS

Thank you for your interest in contributing to **D.E.E.P (Dynamic Executive Edge Platform)**! We welcome contributions that adhere to our engineering rigor, zero-trust security standards, and sovereign computing principles.

---

## 🛠️ Getting Started

1. **Fork the Repository**:
   Click the **Fork** button at the top right of this repository.

2. **Clone your Fork**:
   ```bash
   git clone https://github.com/<your-username>/deep.git
   cd deep
   ```

3. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your local PostgreSQL credentials and Ollama endpoint
   ```

---

## 🔒 Crucial Architectural Directives Before Contributing

All contributions must strictly follow our non-negotiable architectural directives:

1. **Embedded Microcontroller Directives (PIC18F85K22)**:
   - **Mandatory LCD Line 1 Workaround**: Line 1 of the physical board's 16x2 LCD is broken/unreadable. Any user-facing LCD message must be rendered exclusively on **Line 2** (`LCD_Set_Cursor(2, 1)`, addresses `0xC0..0xCF`). Never route primary output to Line 1.
   - **Active Linear Sensor Math**: The temperature sensor on `AN0` (`RA0`) is the Microchip MCP9701-E/TO linear active thermistor ($19.5\text{ mV}/^\circ\text{C}$ slope, $400\text{ mV}$ offset). Never use LM35 formula. Always compute:
     $$T_A = \frac{V_{\text{mV}} - 400.0}{19.5}$$
   - **Pinouts & Data Bus**: 16x2 LCD Data Bus is wired to `PORTH` (`LATH`). Never route LCD data to `PORTD`.

2. **Local Music & Audio Directives**:
   - **Strict Song Title Matching**: When a user asks for a song, it must match against `C:\Users\User\Music`. Never play an unrelated track by an artist if the song title does not match.
   - **Auto-Download Fallback**: Missing songs are downloaded via `yt-dlp` to local storage.
   - **YouTube Exclusivity**: Open YouTube only when the user explicitly requests YouTube, launching strictly in **Google Chrome** via native `os.startfile()`.

3. **Enterprise Zero-Trust & AST Security**:
   - Destructive DDL/DML statements (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) are prohibited in AI queries and must yield `SECURITY_VIOLATION`.
   - Read-only database queries must enforce an automated ceiling of `LIMIT 100`.
   - Never log or transmit raw API keys, private tokens, or passwords (`sanitize_secrets.py`).

4. **Executive Voice Brevity Directive**:
   - Voice TTS feedback must be concise (1–2 natural sentences, under 15 words) with zero raw markdown syntax in speech audio.

---

## 🛠️ Dynamic Tool Forge (v4) Contribution Standards

When contributing new capabilities or tools to [`self_synthesizing_tool_forge.py`](self_synthesizing_tool_forge.py):

- **AST Security Validation**: Tools must pass [`ASTSecurityShield.validate_code()`](self_synthesizing_tool_forge.py). Prohibited modules: `socket`, `pty`, `subprocess`, `winreg`, `ctypes`. Prohibited builtins: `eval`, `exec`, `compile`, `__import__`.
- **Property-Based Fuzz Testing**: Every tool must be auditable via [`FuzzForgeEngine.run_fuzz_audit()`](self_synthesizing_tool_forge.py) across 15 boundary cases with $100\%$ invariant pass rates and execution latency $< 50\text{ms}$.
- **Immutable Snapshots**: Updates must register a version snapshot via [`ToolVersionManager.save_version()`](self_synthesizing_tool_forge.py).

---

## 🌙 Meta-Learning & Machine Dreaming (v4) Contribution Standards

When contributing preference pairs or training routines to [`nightly_meta_learner.py`](nightly_meta_learner.py):

- Support multi-objective loss configurations: `orpo`, `simpo`, `kto`, `dpo`.
- Maintain canonical anchor tasks in [`ElasticWeightConsolidation`](nightly_meta_learner.py) to prevent catastrophic forgetting.
- Preference pairs in `dpo_preference_pairs.jsonl` must include `prompt`, `chosen`, `rejected`, and `category`.

---

## 🧪 Master Test Suite Verification

Before submitting a Pull Request, verify that all test suites pass with 100% green status:

```bash
# Full 10-Pillar Cockpit Audit
python check_deep.py

# Phase 3 & 4 v4 Autonomous Evolutionary Test Suite
python test_phase3_and_4_v4_evolution.py

# Phase 3 & 4 v3 Sovereign Cognitive Test Suite
python test_phase3_and_4_v3_sovereign.py
python test_advanced_phases_3_and_4.py

# Tool Forge & Meta-Learning Base Unit Suites
python test_phase3_tool_forge.py
python test_phase4_meta_learning.py

# Core Intent & Hardware Test Suites
python test_circuit_ui_and_embedded_mcu.py
python test_user_intents_and_skills.py
python test_pillars_1_and_2.py
```

---

## 🌿 Git & Pull Request Guidelines

1. **Branch Naming**:
   - `feat/feature-name` for new capabilities.
   - `fix/bug-fix-description` for bug fixes.
   - `refactor/subsystem-name` for code cleanup.
   - `docs/documentation-update` for documentation changes.

2. **Commit Messages**:
   Follow conventional commits:
   - `feat(forge): implement genetic Pareto mutator for synthesized tools`
   - `fix(mcu): enforce LCD Line 2 defect guard in XC8 compiler engine`
   - `docs: update ARCHITECTURE.md with v4 ORPO meta-learner specifications`

3. **Submitting a Pull Request**:
   - Push your branch to your fork.
   - Open a PR targeting the `main` branch.
   - Fill out the PR description detailing the changes, test results, and hardware compatibility.
