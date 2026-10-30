# 🌌 D.E.E.P — Dynamic Executive Edge Platform

> **Sovereign Local AI Cockpit, Autonomous Cognitive OS, Hardware Controller & Meta-Learning Foundry**

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm%20Noncommercial-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Security: Zero--Trust](https://img.shields.io/badge/Security-Zero--Trust%20AST-orange.svg)](SECURITY.md)
[![Architecture: Sovereign 12--Pillar](https://img.shields.io/badge/Architecture-12--Pillar%20Cognitive%20OS-purple.svg)](ARCHITECTURE.md)
[![Diagnostics: 10/10 Pillars Passed](https://img.shields.io/badge/Diagnostics-10%2F10%20Verified-brightgreen.svg)](check_deep.py)
[![Meta-Learner: v4 Ultra-Evolution](https://img.shields.io/badge/Meta--Learner-v4%20ORPO%2FSimPO-blue.svg)](nightly_meta_learner.py)
[![Tool Forge: v4 Genetic Mutator](https://img.shields.io/badge/Tool%20Forge-v4%20Self--Synthesizing-emerald.svg)](self_synthesizing_tool_forge.py)

---

## 📖 Overview

**D.E.E.P (Dynamic Executive Edge Platform)** is an enterprise-grade, offline-first autonomous artificial intelligence workstation and sovereign executive cockpit. Designed for zero-cloud reliance, D.E.E.P unifies state-of-the-art local Large Language Models (LLMs), multi-objective continuous preference alignment, autonomous self-synthesizing tool creation, physical microcontroller firmware orchestration, computer vision, neural voice sentinels, and AST-guarded OS automation into a single cohesive operating system.

Whether managing low-latency audio playback, executing AST-guarded database queries, evolving local model weights on an NVIDIA RTX GPU via **ORPO / SimPO / KTO / DPO**, or compiling firmware for a physical **PIC18F85K22** trainer, D.E.E.P delivers executive-level sovereign computing on local hardware.

> 📖 **Deep System Architecture**: See **[ARCHITECTURE.md](ARCHITECTURE.md)** for exhaustive diagrams, the 12 Core Architectural Pillars, full REST and WebSocket API specifications, and database schema mappings.

---

## 🏛️ The 12 Sovereign Architectural Pillars

```
                      ┌─────────────────────────────────────────────────────────┐
                      │              D.E.E.P Sovereign Cockpit                  │
                      │             (Flask + WebSockets + PTY)                  │
                      └────────────────────────────┬────────────────────────────┘
                                                   │
         ┌─────────────────────────┼─────────────────────────┼─────────────────────────┐
         │                         │                         │                         │
┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐
│ 🧠 Vector Core  │       │ 🤖 Local Models │       │ 🔬 Embedded MCU │       │ 🎙️ OmniVoice    │
│ • pgvector 1536 │       │ • Ollama Models │       │ • PIC18F85K22   │       │ • Kokoro TTS    │
│ • deep_db (32T) │       │ • Zero-Cloud    │       │ • LCD Line 2    │       │ • <15 Words     │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │                         │                         │
┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐
│ 🎵 Local Music  │       │ ⚡ Hardware Vit. │       │ 🕸️ OS Graph GNN │       │ 🛡️ AST Shield   │
│ • Title Exact   │       │ • RTX A2000 GPU │       │ • Knowledge Map │       │ • DDL Blocker   │
│ • yt-dlp Cache  │       │ • CUDA Active   │       │ • Property Graph│       │ • LIMIT 100     │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
         │                         │                         │                         │
┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐       ┌────────▼────────┐
│ 🌐 Cyber Nexus  │       │ ੴ Sikh Heritage │       │ 🛠️ Tool Forge v4│       │ 🌙 Meta-Learn v4│
│ • PentAGI DAST  │       │ • Nitnem & Bani │       │ • Genetic Mut.  │       │ • ORPO/SimPO/EWC│
│ • Honeypot Sent.│       │ • Gurmukhi OCR  │       │ • Shadow Runner │       │ • LoRA Fusion   │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

### 1. PostgreSQL & Vector Core (`deep_db`)
Permanent cold storage across 32 relational tables with native `pgvector` embeddings (1536-dim) supporting hybrid episodic retrieval and semantic fact verification.

### 2. Local AI Grid (Ollama)
Zero-cloud local inference supporting Hermes 3, Qwen 2.5 Coder, Qwen 2.5-VL, and custom fine-tuned `deep-sovereign:latest` weights with sub-second execution.

### 3. Physical Microcontroller Toolchain (PIC18F85K22 & PICkit 3)
Complete embedded toolchain for the physical PIC18F Trainer board:
- Discovers 36 MPLAB X projects on disk.
- Compiles C firmware via Microchip XC8 compiler.
- Flashes via headless `ipecmd.exe` with USB Mutex locking.
- **Hardware Defect Guard**: Line 1 of the 16x2 LCD is broken on this trainer; all output is strictly routed to **Line 2** (`LCD_Set_Cursor(2, 1)`, addresses `0xC0..0xCF`).
- **Precision Thermistor Math**: Computes Microchip MCP9701 active thermistor temperatures via $T_A = \frac{V_{\text{mV}} - 400.0}{19.5}$ (never LM35 math).

### 4. Autonomous Voice Engine (Kokoro-ONNX & pyttsx3)
Dual co-pilot voice pipeline (Jarvis & Friday) enforcing the **Executive Voice Brevity Directive** (under 15 words spoken, zero raw markdown in audio streams).

### 5. Local Music Engine & Audio Router
Strict title-exact searching against `C:\Users\User\Music`. Automatically downloads missing songs via `yt-dlp` to local storage for offline playback. Opens YouTube strictly in **Google Chrome** via native `os.startfile()` only when explicitly asked.

### 6. Hardware Vitals & GPU VRAM Sentinel
Monitors CPU, RAM, disk, thermal limits, and NVIDIA RTX A2000 GPU VRAM to ensure safe operating conditions before initiating background training loops.

### 7. Hyper-Relational OS & GNN Knowledge Graph
Dynamic entity-relation property graph interconnecting user tasks, code files, hardware components, and operating context.

### 8. Enterprise AI Guardrails & AST Validation
Zero-trust AST static analyzer inspecting every AI query. Mutating queries (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) are blocked with `SECURITY_VIOLATION`. Read-only queries default to `LIMIT 100`.

### 9. Autonomous PentAGI Security Testing & Honeypot
Integrated DAST security scanner scoped strictly to local RFC 1918 subnets (`127.0.0.1`, `192.168.x.x`), backed by silent decoy listeners on ports 2222 and 33060.

### 10. Sovereign Sikh Heritage & Gurbani Multimodal Gateway
Offline-first devotional portal (`/gurbani`) featuring Nitnem banis, phonetic Romanization, Gurmukhi text search, and audio recitation.

### 11. Self-Synthesizing Tool Forge v4 (Autonomous Cognitive Extensibility)
- **Natural Language Tool Synthesis**: The agent writes, tests, and verifies new Python tools dynamically without restarting.
- **Genetic Mutation & Pareto Optimization**: Evaluates mutations (`memoize`, `guard_fastpath`, `doc_type_hints`) against multi-objective fitness functions.
- **Differential Shadow Execution**: Runs adjacent versions side-by-side to ensure zero semantic regression divergence.
- **OpenAPI & MCP Dynamic API Synthesizer**: Transforms REST endpoints and MCP schemas into typed client tools.
- **Runtime Self-Healing Sentinel**: Intercepts runtime exceptions, diagnoses root causes via Reflexion, patches AST, adds regression tests, and hot-swaps live.
- **Property-Based Fuzz Testing**: 15 boundary cases asserting invariants and bounded latency (< 50ms).

### 12. Continuous Meta-Learning & Autonomous Machine Dreaming v4
- **Multi-Objective GPU LoRA Alignment**: Supports **ORPO** (monolithic SFT + odds-ratio loss), **SimPO** (target margin $\gamma = 0.5$), **KTO** (prospect value loss), and **DPO** on local NVIDIA RTX hardware.
- **Online EWC++ Lifelong Learning**: Running Fisher Information Matrix accumulation ($\\gamma = 0.90$) preventing catastrophic forgetting across multiple nights.
- **Adversarial Counterfactual Dreaming**: Generates adversarial failure scenarios during sleep phases to harden model defenses.
- **LoRA Weight Fusion**: Merges adapter weights ($\\Delta W = \frac{\alpha}{r} B \cdot A$) into base representations and compiles `Modelfile.deep_sovereign`.
- **Shadow Canary Benchmark**: Pre-deployment quality & latency validation before automatic Ollama hot-swap.

---

## 🖥️ Interactive Cockpit UI & Studio

Access the cockpit at **`http://localhost:5000`** in your browser.

- **Main Cockpit (`/`)**: Multi-turn chat, system vitals, MCP server status, hardware status, and live log stream.
- **Cognitive Foundry Modal (`⚡ Cognitive Foundry`)**:
  1. *Tool Forge Studio*: Dynamic tool catalog, 1-click fuzz test runner, AST complexity scorecards, genetic mutation optimizer, differential shadow comparator, and version rollback.
  2. *Machine Dreaming HUD*: Alignment objective selector (`ORPO`, `SimPO`, `KTO`, `DPO`), GPU VRAM and Online EWC++ gauges, adversarial counterfactual dream simulator, and LoRA fusion compiler.
- **Holographic Cyber Nexus (`/nexus`)**: Cyber telemetry HUD and network packet monitors.
- **Sikh Heritage Portal (`/gurbani`)**: Offline devotional gateway with audio recitation.

---

## 🚀 Quick Start Guide

### Prerequisites
- **OS**: Windows 10/11 64-bit
- **Python**: 3.10, 3.11, or 3.12 (64-bit)
- **Ollama**: Installed and running locally (`ollama serve`)
- **NVIDIA GPU** *(Recommended)*: RTX A2000 or higher for local LoRA meta-learning

### 1. Clone & Setup Environment
```bash
git clone https://github.com/rsingh287/deep.git
cd deep

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` to set your PostgreSQL credentials and local configuration.

### 3. Launch the Cockpit
```bash
# Launch Flask server & background sentinels
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Comprehensive Diagnostic & Test Matrix

Execute the automated test suites to verify all 12 pillars:

```bash
# Sovereign Cockpit 10-Pillar Diagnostic Audit (Master Health Check)
python check_deep.py

# Phase 3 & 4 v4 Autonomous Evolutionary Test Suite (Mutator, Shadow, OpenAPI, ORPO, EWC++)
python test_phase3_and_4_v4_evolution.py

# Phase 3 & 4 v3 Sovereign Cognitive Test Suite (Fuzz, AST, DAG, SimPO, Self-Play)
python test_phase3_and_4_v3_sovereign.py
python test_advanced_phases_3_and_4.py

# Tool Forge & Meta-Learning Base Unit Suites
python test_phase3_tool_forge.py
python test_phase4_meta_learning.py

# Subsystem & Hardware Test Suites
python test_circuit_ui_and_embedded_mcu.py
python test_user_intents_and_skills.py
python test_pillars_1_and_2.py
python test_pentagi_integration.py
```

---

## 📂 Project Structure

```
deep/
├── app.py                             # Master Flask application, WebSocket router & hotkey sentinel
├── ARCHITECTURE.md                    # 12-pillar architectural specification, schemas & API reference
├── check_deep.py                      # 10-pillar master diagnostic audit (10/10 passed)
├── self_synthesizing_tool_forge.py    # Tool Forge v4 (Genetic Mutator, Shadow Runner, OpenAPI, Self-Healing)
├── nightly_meta_learner.py            # Meta-Learner v4 (ORPO/KTO/SimPO, Online EWC++, Counterfactuals)
├── sleep_phase_dream_engine.py        # REM machine dreaming memory consolidation
├── embedded_mcu_engine.py             # PIC18F85K22 toolchain, LCD Line 2 defect guard, XC8 flasher
├── local_music_engine.py              # Strict title matching, yt-dlp auto-download, Chrome exclusive route
├── enterprise_ai_guardrails.py        # AST SQL mutation blocker & secret scrubber
├── omni_voice_engine.py               # Kokoro-ONNX neural TTS with Executive Brevity directive
├── pentagi_bridge_engine.py           # PentAGI autonomous DAST security testing bridge
├── dynamic_tools/                     # Verified dynamically synthesized Python tools & version history
│   ├── manifest.json                  # Active tool manifest with fuzz scores and complexity grades
│   ├── tests/                         # Auto-generated unit test suites for synthesized tools
│   └── versions/                      # Immutable historical snapshots for 1-click rollback
├── checkpoints/                       # LoRA adapter weights, Online EWC Fisher matrices
├── routes/                            # Modular REST Blueprints
│   ├── tool_forge_bp.py               # Tool Forge v4 endpoints (mutate, shadow_compare, synthesize_openapi)
│   ├── dream_bp.py                    # Meta-Learning v4 endpoints (train_lora, counterfactual, fuse_lora)
│   ├── chat.py                        # Conversational streaming & dual co-pilot reasoning
│   ├── hardware.py                    # MCU status, firmware compilation, and vitals APIs
│   ├── cyber.py                       # Cyber defense, honeypot & PentAGI DAST routes
│   └── gurbani.py                     # Sikh Heritage devotional portal routes
├── templates/                         # Jinja2 Cockpit UI dashboards & modals
│   ├── index.html                     # Primary Cockpit interface
│   ├── modals/toolForgeAndDreamModal.html # Cognitive Foundry v4 Studio modal
│   └── partials/top_bar.html          # Cockpit top navigation bar
└── test_phase3_and_4_v4_evolution.py  # v4 Autonomous Evolutionary test suite
```

---

## 🔒 Security & Privacy

DEEP is built for **absolute data sovereignty**:
- **Zero-Cloud Dependency**: LLM inference, vector searches, voice synthesis, tool synthesis, and hardware controls execute 100% locally on your machine.
- **AST Security Shield**: Synthesized code cannot access network sockets, process spawns, winreg, or Python introspection escape vectors.
- **Secret Sanitization**: All tokens, credentials, and PII are scrubbed prior to logging or storage.

See [SECURITY.md](SECURITY.md) for complete details.

---

## 📜 License

Licensed under the **PolyForm Noncommercial License 1.0.0**. Free for personal use, academic study, research, and noncommercial evaluation. Commercial licensing inquiries: [deep@local.ai](mailto:deep@local.ai).
