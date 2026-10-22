# 🌌 D.E.E.P — Dynamic Executive Edge Platform

> **Sovereign Local AI Cockpit, Autonomous Voice Sentinel & Physical Hardware Controller**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Security: Zero--Trust](https://img.shields.io/badge/Security-Zero--Trust%20AST-orange.svg)](SECURITY.md)
[![Architecture: Event--Driven](https://img.shields.io/badge/Architecture-Event--Driven-purple.svg)](#system-architecture)

---

## 📖 Overview

**D.E.E.P (Dynamic Executive Edge Platform)** is an enterprise-grade, offline-capable local artificial intelligence workstation and hardware cockpit. Designed for zero-cloud reliance, D.E.E.P unifies state-of-the-art local Large Language Models (LLMs), multi-modal computer vision, voice wake-word sentinels, smart home IoT, and direct embedded microcontroller programming (Microchip PIC18F & PICkit 3) into a single cohesive control center.

Whether managing low-latency audio playback, executing AST-guarded database queries, monitoring network threats with a cyber honeypot, or flashing physical MCU firmware over USB, D.E.E.P delivers executive-level sovereign computing on local hardware.

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
     │ 🎙️ Voice & Co-Pilot   │ │ 👁️ Computer Vision   │ │ ⚡ Embedded Hardware  │
     │ • Wake-word Sentinel  │ │ • MediaPipe Gestures  │ │ • PIC18F85K22 Target  │
     │ • Dual AI Co-Pilots   │ │ • Desktop Screen OCR  │ │ • PICkit 3 USB Flasher│
     │ • Executive TTS Engine│ │ • Camera Inspection   │ │ • 16x2 LCD Line 2 Bus │
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

### ⚡ 3. Physical Hardware & Embedded MCU Controller
- **PIC18F Trainer 2 Architecture**: Native toolchain for the Microchip **PIC18F85K22** (80-pin TQFP, 4.9152 MHz external crystal).
- **USB PICkit 3 Flashing Engine**: Deterministic USB mutex locking to compile and flash XC8 firmware via `ipecmd.exe` with zero bus contention.
- **Hardware Pinout Drivers**:
  - **16x2 Character LCD**: 8-bit bus wired to `PORTH` (`RE0` RS, `RE1` EN, `RA4` Backlight). Strict Line 2 rendering protocol (`0xC0..0xCF`).
  - **Sensors**: Microchip **MCP9701-E/TO** linear active thermistor ($19.5\text{ mV}/^\circ\text{C}$ transfer function on `AN0`/`RA0`) with 16-sample ADC smoothing.
  - **Peripherals**: 8-bit Red LED bar on `PORTD`, piezo buzzer on `LATF`, and matrix keypad on `PORTJ`/`PORTC`.

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
├── requirements.txt               # Python package dependencies
├── docker-compose.yml             # Docker stack for Redis, Qdrant, and n8n
├── .env.example                   # Sanitized environment configuration template
├── routes/                        # Modular Flask Blueprints
│   ├── chat.py                    # Multi-turn dual co-pilot conversational routes
│   ├── hardware.py                # PIC18F MCU flashing & telemetry endpoints
│   ├── vision.py                  # Computer vision and screen inspection APIs
│   ├── cyber.py                   # Cyber defense, honeypot & RBAC routes
│   ├── system.py                  # Process monitoring, health & diagnostics
│   └── ingestion.py               # Document parsing & knowledge base intake
├── intents/                       # Autonomous intent engines
├── pic_firmware/                  # Microchip PIC18F C source templates & hex binaries
├── pcb_projects/                  # PCB designs & Gerber generation templates
├── static/                        # CSS, Vanilla JS, and Cockpit UI assets
├── templates/                     # Jinja2 cockpit UI dashboards and partials
├── tests/                         # Comprehensive system and security test suites
├── CONTRIBUTING.md                # Contribution guidelines and coding conventions
├── SECURITY.md                    # Zero-trust security policy & vulnerability reporting
└── LICENSE                        # MIT Open Source License
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

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.
