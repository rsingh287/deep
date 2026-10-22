# Workspace AI Agent Rules

## Music & Audio Playback Directives

1. **Local Library Priority & Strict Song Title Matching**:
   - Whenever the user asks for a specific song (e.g. `play <song>`, `play <song> by <singer>`, `<singer> <song>`):
     - The **SONG TITLE** must match the local library (`C:\Users\User\Music`).
     - **NEVER** play an arbitrary local track simply because the singer's name matches if the requested song title is missing.
     - Only if the user explicitly asks for the *singer only* without a specific song (e.g. `play songs by <singer>`, `play <singer>`) is it permitted to play an available track by that artist.
   - If the specific song is found locally, play it immediately on PC Speakers.

2. **Automatic Download & Playback Fallback for Missing Songs**:
   - If the specific song requested is NOT in the local library:
     - Automatically download the exact requested track directly to `C:\Users\User\Music` using `yt-dlp` via `local_music_engine.download_and_play_track(query)`.
     - Play the downloaded MP3 locally through PC Speakers.
     - Do NOT open YouTube or the browser for general song/singer requests.

3. **Strict YouTube Exclusivity**:
   - ONLY open YouTube if the user explicitly specifies YouTube (e.g., "open on youtube", "play on youtube", "in youtube", "open youtube and play ...").
   - When explicitly opening YouTube, launch it specifically in **Google Chrome** using native `os.startfile(chrome_bin, arguments=url)` to ensure it opens visibly on the interactive desktop without cmd quote escaping errors (`Windows cannot find '\\'`).
   - Chrome routes to PC Speakers; Microsoft Edge remains dedicated to Cockpit UI and headphone mic/speaker.

---

## Enterprise-Grade System Directives

1. **Zero-Trust Security & Pre-Flight Sanitization**:
   - Before logging, transmitting prompts, or displaying terminal outputs, automatically scrub sensitive credentials, passwords, and private tokens via `sanitize_secrets.py` and `pii_ner_extractor_engine.py`.
   - Never log or speak API keys or plain credentials.

2. **AST-Enforced Safe Database Execution**:
   - AI-generated queries must validate against `enterprise_ai_guardrails.py`.
   - DDL/DML mutations (`DROP`, `DELETE`, `TRUNCATE`, `ALTER`) are blocked; queries must be read-only with an enforced default `LIMIT 100`.

3. **Circuit Breakers & Non-Blocking Asynchronous SLA**:
   - Heavy tasks (`yt-dlp` downloads, model inference, video encoding, web scraping) must run on asynchronous background threads.
   - The main Flask and voice listener threads must never block (main-loop latency $\le 50\text{ms}$).
   - External network endpoints (Kasa smart devices, external APIs) must fail fast with hard timeouts ($\le 1.5\text{s}$) to avoid hanging the UI.

4. **Hardware Resource Mutex (Webcam & Audio Handles)**:
   - Camera (`cv2.VideoCapture`) and audio stream handles must be acquired and deterministically released inside `finally` blocks to prevent `Device busy` lockouts.
   - Separate vision engines (MJPEG streaming, hardware inspection, gesture detection) must coordinate access.

5. **Executive Voice Brevity Directive (Audio Noise Reduction)**:
   - Spoken feedback via TTS must be concise (1–2 natural sentences, under 15 words).
   - Prohibited from voice output: raw Markdown (`*`, `#`, `` ` ``), URLs, raw JSON, Python tracebacks, and terminal dumps. Detailed data must go strictly to the Cockpit UI.

6. **Human-in-the-Loop (HITL) Gate for Destructive Actions**:
   - Require explicit verbal or button confirmation before deleting files permanently, closing active user application windows, or rebooting the PC.

---

## Embedded & Microcontroller Directives (PIC18F85K22 & PICkit 3)

1. **Physical Hardware Profile (PIC18F Trainer 2 Rev 1.24)**:
   - Target MCU: Microchip PIC18F85K22 (80-pin TQFP, 64KB Flash, 3.8KB RAM, 1024B EEPROM, 12-bit ADC).
   - Clock Frequency: 4.9152 MHz external crystal (`#define _XTAL_FREQ 4915200`, `#pragma config FOSC = HS2`).
   - Debugger/Programmer: Microchip PICkit 3 (`BUR181916585`).

2. **Mandatory LCD Line 1 Hardware Defect Workaround**:
   - Line 1 (`0x80..0x8F`) of the 16x2 LCD is broken/unreadable on this board.
   - **STRICT DIRECTIVE**: All user-facing UI, status messages, sensor readings, and timers must be rendered solely on **Line 2** (`LCD_Set_Cursor(2, 1)`, `0xC0..0xCF`, max 16 chars). Never leave primary information on Line 1.

3. **Accurate Board Pinouts & Bus Protocols**:
   - **16x2 LCD Data Bus**: Full 8-bit mode wired to **`PORTH` (`LATH`)** (`TRISH = 0x00;`). NEVER route LCD data to PORTD!
   - **16x2 LCD Control**: `RE0` = RS (`LATEbits.LATE0`), `RE1` = EN (`LATEbits.LATE1`).
   - **16x2 LCD Backlight**: Wired to **`RA4`** (`TRISAbits.TRISA4 = 0; LATAbits.LATA4 = 0;` turns Backlight **ON**).
   - **Red LED Bar**: 8 discrete LEDs wired to **`PORTD` (`LATD`)** (`TRISD = 0x00;`).
   - **Piezo Buzzer**: Driven on `LATF` / `LATAbits.LATA5` / `LATCbits.LATC3` (RA4 is reserved exclusively for LCD Backlight).
   - **Keypad**: Keypad rows (`PORTJ[2:0]`) and columns (`PORTC[2:0]`) require `#pragma config SOSCSEL = DIG` to free `RC0` and `RC1` from the secondary oscillator.

4. **Sensor Transfer Function Precision (MCP9701-E/TO)**:
   - The onboard analog temperature sensor on `AN0` (`RA0`) is the Microchip MCP9701-E/TO linear active thermistor ($19.5\text{ mV}/^\circ\text{C}$ slope, $400\text{ mV}$ offset at $0^\circ\text{C}$).
   - **NEVER** use LM35 math ($10\text{ mV}/^\circ\text{C}$). Always compute:
     $$T_A = \frac{V_{\text{mV}} - 400.0}{19.5}$$
   - Apply a minimum 16-sample rolling ADC average to filter high-frequency switching noise.

5. **PICkit 3 Flashing Protocol & USB Mutex**:
   - Only one process can communicate with the PICkit 3 over USB at a time.
   - In MPLAB X IDE, flash using `F6` (Make and Program Device).
   - In headless CLI mode via `ipecmd.exe`, ensure MPLAB X is disconnected or closed before invoking:
     `ipecmd.exe -P18F85K22 -TPPK3 -TSBUR181916585 -M -F"<path_to_hex>" -OL`
   - If `Device ID (00000000)` appears, alert the user to verify the 5V/9V DC adapter on the trainer board.

