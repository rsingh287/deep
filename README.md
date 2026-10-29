# 🌌 D.E.E.P — Dynamic Executive Edge Platform

> **Sovereign Local AI Cockpit, Autonomous Voice Sentinel & Physical Hardware Controller**

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm%20Noncommercial-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Security: Zero--Trust](https://img.shields.io/badge/Security-Zero--Trust%20AST-orange.svg)](SECURITY.md)
[![Architecture: Event--Driven](https://img.shields.io/badge/Architecture-Event--Driven-purple.svg)](ARCHITECTURE.md)
[![Diagnostics: 10/10 Pillars Passed](https://img.shields.io/badge/Pillars-10%2F10%20Verified-brightgreen.svg)](check_deep.py)

---

## 📖 Overview

**D.E.E.P (Dynamic Executive Edge Platform)** is an enterprise-grade, offline-capable local artificial intelligence workstation and autonomous executive cockpit. Designed for zero-cloud reliance, D.E.E.P unifies state-of-the-art local Large Language Models (LLMs), multi-modal computer vision, voice wake-word sentinels, smart home IoT, and autonomous OS desktop automation into a single cohesive control center.

Whether managing low-latency audio playback, executing AST-guarded database queries, monitoring network threats with a cyber honeypot, or orchestrating local agentic workflows, D.E.E.P delivers executive-level sovereign computing on local hardware.

> 📖 **System Architecture & Deep Dive**: See **[ARCHITECTURE.md](ARCHITECTURE.md)** for exhaustive diagrams, the 10 Core Architectural Pillars, full REST and WebSocket API specifications, and database schema mappings.

---

## ✨ Key Capabilities

```
                      ┌─────────────────────────────────────────┐
                      │        D.E.E.P Sovereign Cockpit        │
                      │       (Flask + WebSockets + PTY)        │
                      └────────────────────┬────────────────────┘
                                           │
                 ┌─────────────────────────┼─────────────────────────┐
                 │                         │                         │
     ┌───────────▼───────────┐ ┌───────────▼───────────┐ ┌───────────▼───────────┐
     │ 🎙️ Voice & Co-Pilot   │ │ 👁️ Computer Vision   │ │ ⚙️ OS & Agent Pilot   │
     │ • Wake-word Sentinel  │ │ • MediaPipe Gestures  │ │ • Autonomous Workflow │
     │ • Dual AI Co-Pilots   │ │ • Desktop Screen OCR  │ │ • Native Shell / PTY  │
     │ • Executive TTS Engine│ │ • Camera Inspection   │ │ • Everyday PC Actions │
     └───────────────────────┘ └───────────────────────┘ └───────────────────────┘
                 │                         │                         │
     ┌───────────▼───────────┐ ┌───────────▼───────────┐ ┌───────────▼───────────┐
     │ 🧠 Knowledge & Memory │ │ 🛡️ Zero-Trust Defense │ │ 🏡 IoT & Ambient Media│
     │ • Qdrant Vector DB    │ │ • AST Query Guardrail │ │ • TP-Link Kasa Relays │
     │ • Knowledge Graph     │ │ • Secret Sanitization │ │ • Local DJ Engine     │
     │ • Episodic Recall     │ │ • Cyber Honeypot Sentry││ • Strict Title Match  │
     └───────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

### 🎙️ 1. Voice Master Sentinel & Dual Co-Pilots
- **Wake-Word Daemon**: Low-overhead continuous listener running on a dedicated thread for instant verbal activation.
- **Dual Co-Pilot Core**: Real-time collaborative reasoning between **J.A.R.V.I.S.** (Executive Butler) and **F.R.I.D.A.Y.** (Tactical Operations).
- **Executive Voice Brevity**: Automatic audio noise reduction delivering crisp, 1–2 sentence verbal responses without raw formatting noise.

### 👁️ 2. Multi-Modal Vision & Gesture Kinematics
- **Desktop Pilot Vision**: Live screen capture and regional OCR analysis for hands-free computer control.
- **MediaPipe Hand & Face Tracking**: Zero-latency physical gesture recognition for contactless system navigation.
- **Hardware Inspection Stream**: MJPEG video feed for real-time circuit board, wire, and component diagnostics.

### ⚙️ 3. OS Automation & Autonomous Agent Pilot
- **Everyday PC Operations**: Deep desktop automation supporting application launching, window management, audio controls, and workflow execution.
- **PTY Terminal Bridge**: Interactive WebSocket-based terminal session with ANSI color rendering and zero-latency shell communication.
- **Hardware Telemetry Sentinel**: Real-time monitoring of CPU, RAM, GPU metrics, disk health, and thermal levels.

### 🧠 4. Epistemic Vector Memory & RAG
- **Qdrant Vector Engine**: Ultra-fast vector database storage for semantic memory and contextual document retrieval.
- **Persistent Knowledge Graph**: Relational cross-referencing between user interactions, technical concepts, and operating context.
- **Local LLM Integration**: Pluggable backend supporting Ollama (Llama 3.2, Qwen 2.5, DeepSeek) with zero external API dependencies.

### 🛡️ 5. Enterprise Zero-Trust & Cyber Defense
- **Pre-Flight Sanitization**: Inbound and outbound streams are scrubbed of credentials, private tokens, and PII prior to logging.
- **AST-Enforced Safe Execution**: AI-generated SQL queries are parsed through Python AST trees—blocking destructive mutations (`DROP`, `DELETE`, `TRUNCATE`) and enforcing read ceilings (`LIMIT 100`).
- **Network Sentinel & Honeypot**: Embedded decoy endpoints to monitor unauthorized LAN scanning or lateral network intrusion.

### 🎵 6. Local Music Engine & DJ
- **Local Library Strict Matching**: Scans and indexes local audio (`C:\Users\User\Music`) with strict song title verification.
- **Autonomous Download Fallback**: If a requested song is missing, `yt-dlp` automatically downloads the track directly to local storage for offline playback.
- **Hardware Speaker Routing**: Direct playback to primary PC speakers without browser hijacking.

### 🔌 7. Embedded Microcontroller Toolchain (PIC18F85K22 & PICkit 3)
- **Physical Trainer Integration**: Dedicated driver `embedded_mcu_engine.py` communicating with PIC18F85K22 (4.9152 MHz external crystal, HS2 mode).
- **Automated Hex Compilation & Flashing**: Native headless invocation of Microchip `ipecmd.exe` with PICkit 3 USB hardware lock handling.
- **Hardware Defect Workaround**: Automatic enforcement of LCD Line 2 cursor rendering (`0xC0..0xCF`), bypassing defective Line 1 hardware on the trainer.
- **High-Precision Sensor Math**: Implements exact MCP9701-E/TO linear transfer formula ($T_A = \frac{V_{\text{mV}} - 400.0}{19.5}$) with 16-sample rolling ADC noise filtering.

### ⚡ 8. Enterprise Resilience & Hystrix Circuit Breakers
- **Stateful Fail-Fast Protection**: `hystrix_circuit_breaker.py` protects critical endpoints (`ollama_inference`, `iot_smart_home`, `screen_vision`, `mcu_flasher`).
- **Dynamic State Transitions**: Automatically transitions between `CLOSED`, `OPEN` ($\le 1.5\text{s}$ timeout), and `HALF-OPEN` recovery probes.
- **Telemetry Exposure**: Real-time circuit breaker metrics exposed via `GET /api/system/circuit_breakers`.

### 🛡️ 9. PentAGI Autonomous DAST Penetration Testing
- **Agentic Vulnerability Assessment**: Integrated bridge `pentagi_bridge_engine.py` connecting D.E.E.P to Dockerized PentAGI workflows.
- **Controlled DAST Scans**: REST endpoints (`/api/cyber/pentagi/status`, `/api/cyber/pentagi/start`, `/api/cyber/pentagi/stop`) for local network security auditing and compliance verification.

### 💤 10. Multi-Tier Cognitive Memory & REM Machine Dreaming
- **Tier 1 (Qdrant Hot Session Cache)**: Low-latency in-memory session cache via `qdrant_session_cache.py` for immediate conversational context.
- **Tier 2 (PostgreSQL pgvector Deep DB)**: Permanent cold storage across 32 relational tables with vector similarity search.
- **REM Dreaming Consolidation**: `sleep_phase_dream_engine.py` runs during system idle to distill session logs into factual triples and DPO training pairs in `dataset_fine_tune.jsonl`.
- **Zero-Copy Frame Buffer**: `shared_memory_frame_buffer.py` provides a 12MB shared-memory IPC buffer between vision engines and Flask.

### 🌌 11. Holographic Cyber Nexus & Sikh Heritage Portals
- **Holographic Cyber Nexus (`/nexus`)**: Real-time visual network matrix, cyber telemetry HUD, and packet flow monitors.
- **Sikh Heritage Portal (`/gurbani`)**: Offline-first devotional repository, phonetically accurate Romanized and Gurmukhi search with audio recitation.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12 (64-bit recommended)
- **Node.js**: v18+ (for optional MCP servers)
- **Ollama**: Installed and running locally (`ollama serve`)
- **Docker** *(Optional)*: For Redis, Qdrant, and n8n container stack

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/deep.git
cd deep
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the example environment template:
```bash
cp .env.example .env
```
Edit `.env` to customize your local ports, database credentials, or optional messaging tokens.

### 5. Launch the Cockpit
```bash
# Direct Python launch
python app.py

# Or via Windows launch batch script
.\start.bat
```
Navigate to **`http://localhost:5000`** in your browser to enter the DEEP sovereign cockpit.

---

## 🐳 Docker Infrastructure (Optional)

To launch the integrated vector storage, task queue, and workflow orchestrator:
```bash
docker-compose up -d
```
This spins up:
- **Qdrant Vector Database**: `http://localhost:6333`
- **Redis Cache & Queue**: `localhost:6379`
- **n8n Workflow Automation**: `http://localhost:5678`

---

## 📂 Project Structure

```
deep/
├── app.py                         # Primary Flask application & WebSocket PTY router
├── ARCHITECTURE.md                # Authoritative 10-pillar architecture, schema & API spec
├── check_deep.py                  # Comprehensive 10-pillar diagnostic suite (10/10 green)
├── requirements.txt               # Python package dependencies
├── docker-compose.yml             # Docker stack for Redis, Qdrant, and n8n
├── .env.example                   # Sanitized environment configuration template
├── embedded_mcu_engine.py         # Microchip PIC18F85K22 & PICkit 3 flashing toolchain
├── hystrix_circuit_breaker.py     # Enterprise fail-fast circuit breakers
├── pentagi_bridge_engine.py       # Autonomous PentAGI DAST testing bridge
├── qdrant_session_cache.py        # Tier 1 in-memory hot session vector cache
├── sleep_phase_dream_engine.py    # Autonomous REM machine dreaming memory consolidation
├── shared_memory_frame_buffer.py  # 12MB zero-copy camera frame buffer IPC
├── routes/                        # Modular Flask Blueprints
│   ├── chat.py                    # Multi-turn dual co-pilot conversational routes & SSE stream
│   ├── hardware.py                # System hardware telemetry, battery & MCU status APIs
│   ├── vision.py                  # Computer vision and screen inspection APIs
│   ├── cyber.py                   # Cyber defense, honeypot & PentAGI DAST routes
│   ├── system.py                  # Process monitoring, health & circuit breaker metrics
│   ├── gurbani.py                 # Sikh Heritage portal routes & search endpoints
│   └── ingestion.py               # Document parsing & knowledge base intake
├── intents/                       # Autonomous intent engines (registry, pentest, os, etc.)
├── static/                        # CSS, Vanilla JS, and Cockpit UI assets
├── templates/                     # Jinja2 cockpit UI dashboards and partials
├── tests/                         # Comprehensive system and security test suites
├── CONTRIBUTING.md                # Contribution guidelines and coding conventions
├── SECURITY.md                    # Zero-trust security policy & vulnerability reporting
└── LICENSE                        # PolyForm Noncommercial 1.0.0 License
```

---

## 🧪 Diagnostics & System Verification

D.E.E.P includes a built-in automated test and diagnostic harness to verify all system components, hardware interfaces, database engines, and resilience breakers.

### Running the Master 10-Pillar Diagnostic Suite
```bash
python check_deep.py
```
This runs automated health checks across all 10 core pillars:
1. **PostgreSQL & pgvector** (`deep_db` 32-table relational schema + vectors)
2. **Local Ollama LLM Inference** (Qwen 2.5, Hermes 3, DeepSeek models)
3. **Embedded MCU Engine** (PIC18F85K22 board pinouts, LCD Line 2 defect workaround, MCP9701 sensor math)
4. **OmniVoice & Audio Subsystem** (Voice sentinels and TTS engine)
5. **Local DJ & Strict Song Matcher** (`C:\Users\User\Music` indexer and yt-dlp fallback)
6. **Hardware Telemetry & GPU Acceleration** (NVIDIA CUDA / GPU status)
7. **PC Brain GNN Hyper-Graph** (Knowledge graph relations)
8. **AST Query Security Guardrails** (DDL/DML blocker and read ceiling enforcement)
9. **Cyber Nexus & Honeypot Engine** (Decoy sentinels and threat scoring)
10. **Public APIs & Offline Resilience** (Weather, finance, fallback services)

### Running Targeted Test Suites
```bash
# Verify Circuit Breakers and PIC18F85K22 Embedded MCU
python test_circuit_ui_and_embedded_mcu.py

# Verify Multi-Tier Memory (Qdrant Hot Cache & REM Dreaming)
python test_pillars_1_and_2.py

# Verify PentAGI DAST Bridge & Dynamic Testing Endpoints
python test_pentagi_integration.py

# Verify Autonomous User Intents and Tool Registry
python test_user_intents_and_skills.py
```

---

## 🔒 Security & Privacy

DEEP is built from the ground up for **sovereign computing**:
- **Offline First**: All core processing (inference, vector search, voice, vision, hardware control) runs on your local machine.
- **No Telemetry Leaks**: System metrics, prompts, and database records remain strictly within your local environment.
- **Pre-Flight Scrubber**: Sensitive credentials, passwords, and private tokens are automatically scrubbed via `sanitize_secrets.py`.

See [SECURITY.md](SECURITY.md) for full details on our zero-trust architecture.

---

## 📜 License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**. 

- ✅ **Free & Permitted**: Personal use, academic study, research, hobbyist tinkering, and noncommercial evaluation.
- 🚫 **Prohibited**: Any commercial deployment, SaaS monetization, paid distribution, or commercial integration without a separate commercial license from the author.

See the [LICENSE](LICENSE) file for complete legal terms. For commercial licensing inquiries, contact [deep@local.ai](mailto:deep@local.ai).
