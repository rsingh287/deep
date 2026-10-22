"""
Microchip PIC18F85K22 & PICkit 3 Embedded Intelligence Engine
Deep Local AI PC Cockpit & Autonomous Hardware Sentinel
Author: D.E.E.P Workstation / Antigravity AI
"""

import os
import re
import json
import subprocess
import psutil

# Microchip Toolchain Locations on this Workstation
MPLABX_PATH = r"C:\Program Files (x86)\Microchip\MPLABX\v5.35"
XC8_CC_PATH = r"C:\Program Files\Microchip\xc8\v3.10\bin\xc8-cc.exe"
MAKE_PATH = os.path.join(MPLABX_PATH, r"gnuBins\GnuWin64\bin\make.exe")
IPECMD_PATH = os.path.join(MPLABX_PATH, r"mplab_platform\mplab_ipe\ipecmd.exe")
MPLAB_IDE_EXE = os.path.join(MPLABX_PATH, r"mplab_platform\bin\mplab_ide64.exe")

PROJECTS_DIR = r"C:\Users\User\MPLABXProjects"
DEFAULT_SERIAL = "BUR181916585"
TARGET_PART = "18F85K22"
XTAL_FREQ_HZ = 4915200  # 4.9152 MHz crystal oscillator


def get_board_specs():
    """Returns the exact physical hardware profile and pin assignments of the PIC18F Trainer 2 Rev 1.24."""
    return {
        "board_name": "PIC18F Trainer 2 Rev 1.24",
        "mcu": "Microchip PIC18F85K22 (80-Pin TQFP)",
        "oscillator": "4.9152 MHz Precision Crystal (HS2 Mode)",
        "programmer": f"Microchip PICkit 3 (Serial: {DEFAULT_SERIAL})",
        "power_input": "5.0V DC Regulated (External DC Barrel Jack)",
        "peripherals": {
            "lcd": {
                "controller": "HD44780 compatible (16x2)",
                "data_mode": "8-bit (LATH / PORTH D0..D7, TRISH=0x00)",
                "control": "RE0=RS (LATEbits.LATE0), RE1=EN (LATEbits.LATE1)",
                "backlight": "RA4 (LATAbits.LATA4, TRISAbits.TRISA4=0, drive 0 for ON)",
                "defect_alert": "LINE 1 (0x80..0x8F) IS PHYSICALLY DAMAGED/UNREADABLE. ALL DISPLAY ROUTINES MUST RENDER EXCLUSIVELY ON LINE 2 (0xC0..0xCF, 16 chars).",
                "bus_rule": "LCD data bus is wired exclusively to PORTH (LATH). Never write LCD data to PORTD (PORTD is the 8 Red LED Bar)."
            },
            "temperature_sensor": {
                "ic": "Microchip MCP9701-E/TO (Active Linear Thermistor)",
                "pin": "AN0 / RA0 (Pin 24)",
                "transfer_formula": "V_out(mV) = (19.5 mV/C * Temp) + 400 mV",
                "temp_formula": "Temp(C) = (V_out(mV) - 400.0) / 19.5",
                "room_temp_mv": 820.0,
                "warning": "DO NOT use LM35 math (10 mV/C); using LM35 causes false 82C readings at room temp."
            },
            "keypad": {
                "type": "3x3 Matrix Keypad",
                "rows": "PORTB[4:2] (RB2, RB3, RB4 inputs with weak pull-ups RBPU=0)",
                "columns": "PORTC[2:0] (RC0, RC1, RC2 outputs driven low sequentially)",
                "config_requirement": "#pragma config SOSCSEL = DIG is mandatory to free RC0/RC1 from secondary oscillator."
            },
            "seven_segment": {
                "digits": 2,
                "multiplexed": True,
                "cathodes": "LATE[7:0] segments a..g",
                "anodes": "LATHbits.LATH0 and LATHbits.LATH1 digit selectors"
            },
            "analog_pots": {
                "RV1": "AN1 / RA1",
                "RV2": "AN2 / RA2"
            },
            "buzzer": {
                "pin": "LATF / LATAbits.LATA5 / LATCbits.LATC3 (RA4 is reserved for LCD Backlight)"
            },
            "led_bar": {
                "count": 8,
                "port": "PORTD (LATD[7:0], TRISD=0x00)"
            },
            "dip_switches": {
                "count": 8,
                "port": "PORTJ (Pins float when open; needs software debounce or pullup emulation)"
            }
        }
    }


def detect_pickit3():
    """Detects if the Microchip PICkit 3 is connected via USB and checks if MPLAB X is currently running."""
    res = {
        "connected": False,
        "serial": DEFAULT_SERIAL,
        "friendly_name": None,
        "mplab_ide_running": False,
        "mplab_pid": None,
        "status": "Checking..."
    }

    # 1. Check if MPLAB X IDE process is running
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if "mplab_ide" in proc.info['name'].lower():
                res["mplab_ide_running"] = True
                res["mplab_pid"] = proc.info['pid']
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 2. Check Windows PnP device list via PowerShell
    try:
        ps_cmd = (
            "Get-PnpDevice -PresentOnly | "
            "Where-Object { $_.FriendlyName -match 'PICkit|Microchip|ICD|BUR181916585' -or $_.DeviceID -match 'VID_04D8' } | "
            "Select-Object -First 3 FriendlyName, Status, DeviceID | ConvertTo-Json"
        )
        p = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=4
        )
        if p.returncode == 0 and p.stdout.strip():
            data = json.loads(p.stdout)
            if isinstance(data, list) and len(data) > 0:
                dev = data[0]
            elif isinstance(data, dict):
                dev = data
            else:
                dev = None

            if dev:
                res["connected"] = True
                res["friendly_name"] = dev.get("FriendlyName", "Microchip PICkit 3 In-Circuit Debugger")
                res["status"] = dev.get("Status", "OK")
    except Exception as e:
        res["error"] = str(e)

    # 3. Refine Status Message
    if res["connected"]:
        if res["mplab_ide_running"]:
            res["status_message"] = (
                f"✅ PICkit 3 ({res['serial']}) ACTIVE & LOCKED BY MPLAB X (PID {res['mplab_pid']}). "
                f"Press F6 in MPLAB X to flash, or close MPLAB X for CLI ipecmd flashing."
            )
        else:
            res["status_message"] = (
                f"✅ PICkit 3 ({res['serial']}) CONNECTED & READY for direct CLI flashing via ipecmd."
            )
    else:
        res["status_message"] = (
            "⚠️ PICkit 3 USB hardware not detected in PnP table. Ensure USB mini-B cable is firmly seated."
        )

    return res


def list_workspace_projects():
    """Lists all MPLAB X projects in C:\\Users\\User\\MPLABXProjects with build status."""
    if not os.path.exists(PROJECTS_DIR):
        return []

    projects = []
    for item in os.listdir(PROJECTS_DIR):
        full_path = os.path.join(PROJECTS_DIR, item)
        if os.path.isdir(full_path) and item.endswith(".X"):
            p_name = item[:-2]
            c_file = os.path.join(full_path, f"{p_name}.c")
            if not os.path.exists(c_file):
                # Search for any .c file
                c_files = [f for f in os.listdir(full_path) if f.endswith(".c")]
                c_file = os.path.join(full_path, c_files[0]) if c_files else None

            hex_file = os.path.join(full_path, "dist", "default", "production", f"{item}.production.hex")
            has_hex = os.path.exists(hex_file)
            hex_size = os.path.getsize(hex_file) if has_hex else 0

            projects.append({
                "project_dir": item,
                "project_name": p_name,
                "source_c": c_file,
                "hex_file": hex_file if has_hex else None,
                "hex_size_bytes": hex_size,
                "is_built": has_hex
            })

    return projects


def compile_project(project_name_or_dir):
    """Compiles an MPLAB X project using GnuWin64 make.exe and XC8 v3.10."""
    dir_name = project_name_or_dir if project_name_or_dir.endswith(".X") else f"{project_name_or_dir}.X"
    project_path = os.path.join(PROJECTS_DIR, dir_name)

    if not os.path.exists(project_path):
        return {"success": False, "error": f"Project directory not found: {project_path}"}

    if not os.path.exists(MAKE_PATH):
        return {"success": False, "error": f"Make binary not found at: {MAKE_PATH}"}

    cmd = [
        MAKE_PATH,
        "-f",
        "nbproject/Makefile-default.mk",
        "SUBPROJECTS=",
        ".build-conf"
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        hex_file = os.path.join(project_path, "dist", "default", "production", f"{dir_name}.production.hex")
        built = os.path.exists(hex_file)

        return {
            "success": proc.returncode == 0 and built,
            "returncode": proc.returncode,
            "hex_path": hex_file if built else None,
            "hex_size_bytes": os.path.getsize(hex_file) if built else 0,
            "stdout": proc.stdout[-2000:] if proc.stdout else "",
            "stderr": proc.stderr[-2000:] if proc.stderr else ""
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def flash_firmware(hex_path, target_part=TARGET_PART, serial=DEFAULT_SERIAL):
    """Flashes a compiled HEX file using ipecmd.exe to the PICkit 3."""
    if not os.path.exists(hex_path):
        return {"success": False, "error": f"HEX file does not exist: {hex_path}"}

    # Check USB mutex: Is MPLAB X IDE running?
    p_status = detect_pickit3()
    if p_status.get("mplab_ide_running"):
        return {
            "success": False,
            "error": "USB_MUTEX_LOCKED",
            "message": (
                f"MPLAB X IDE (PID {p_status.get('mplab_pid')}) is actively open and owns the PICkit 3 USB handle.\n"
                f"To program:\n"
                f"1. Inside MPLAB X, simply press F6 (Make and Program Device Main Project).\n"
                f"2. Or close MPLAB X to allow automated command-line flashing via ipecmd."
            )
        }

    cmd = [
        IPECMD_PATH,
        f"-P{target_part}",
        "-TPPK3",
        f"-TS{serial}",
        "-M",
        f"-F{hex_path}",
        "-OL"
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=40
        )
        output = proc.stdout + "\n" + proc.stderr
        success = "Programming/Verify complete" in output or "Program Succeeded" in output or "Operation Succeeded" in output

        return {
            "success": success,
            "output": output,
            "returncode": proc.returncode
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def audit_c_code(c_source_code):
    """
    Automated pre-flight linter checking hardware rules:
    - Line 1 LCD usage (Hardware defect)
    - LM35 vs MCP9701 math error
    - SOSCSEL = DIG missing
    - Crystal oscillator frequency
    """
    warnings = []
    errors = []

    # 1. Check for Line 1 LCD writes
    if re.search(r"LCD_Set_Cursor\s*\(\s*1\s*,", c_source_code):
        errors.append(
            "CRITICAL HARDWARE BUG: Detected call to LCD_Set_Cursor(1, ...). "
            "Line 1 of the 16x2 LCD on this board is broken/unreadable. "
            "All output MUST be targeted to Line 2: LCD_Set_Cursor(2, 1)."
        )
    if re.search(r"LCD_Cmd\s*\(\s*0x8[0-9A-Fa-f]\s*\)", c_source_code):
        errors.append(
            "CRITICAL HARDWARE BUG: Detected DDRAM command 0x8X (Line 1 address). Target 0xC0 (Line 2) instead."
        )

    # 2. Check for LM35 formula (10 mV/C)
    if re.search(r"10\.0\s*f?", c_source_code) and re.search(r"temp", c_source_code, re.I):
        if not re.search(r"19\.5", c_source_code):
            errors.append(
                "CRITICAL SENSOR BUG: Code appears to use LM35 math (10 mV/C). "
                "The onboard sensor is a Microchip MCP9701-E/TO (19.5 mV/C slope, 400 mV offset). "
                "Formula must be: Temp = (V_mV - 400.0) / 19.5."
            )

    # 3. Check for SOSCSEL = DIG
    if "SOSCSEL = DIG" not in c_source_code:
        warnings.append(
            "CONFIGURATION WARNING: #pragma config SOSCSEL = DIG is missing. "
            "RC0/RC1 will default to secondary oscillator, rendering Keypad Columns 1 & 2 inoperative."
        )

    # 4. Check Crystal Frequency
    if "_XTAL_FREQ 4915200" not in c_source_code:
        warnings.append(
            "TIMING WARNING: #define _XTAL_FREQ 4915200 not found. Trainer crystal is 4.9152 MHz. "
            "Inaccurate frequency definition will cause __delay_ms() and timer overflows to run at wrong speeds."
        )

    # 5. Check LCD Data Bus (PORTH vs PORTD)
    if ("LCD" in c_source_code or "lcd" in c_source_code) and "LATD" in c_source_code and "LATH" not in c_source_code:
        errors.append(
            "CRITICAL PINOUT BUG: LCD data bus on this board is wired to PORTH (LATH), NOT PORTD! "
            "PORTD controls the 8 Red LED bar. Driving LCD signals to LATD causes a blank screen."
        )

    # 6. Check LCD Backlight (RA4 = 0)
    if ("LCD" in c_source_code or "lcd" in c_source_code) and "LATA4" not in c_source_code and "LATA" not in c_source_code:
        warnings.append(
            "HARDWARE WARNING: LCD Backlight pin RA4 should be initialized (TRISAbits.TRISA4 = 0; LATAbits.LATA4 = 0;) "
            "to ensure the LCD display is illuminated and visible."
        )

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def scaffold_and_compile_project(project_name, c_source_code):
    """
    Scaffolds a new MPLAB X project for PIC18F85K22, writes the C code,
    runs pre-flight audit, compiles it via make.exe / XC8, and loads it into MPLAB X.
    """
    import shutil

    clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", project_name).strip("_")
    if not clean_name:
        clean_name = "pic_firmware"

    # 1. Pre-flight hardware audit
    audit = audit_c_code(c_source_code)

    project_dir = os.path.join(PROJECTS_DIR, f"{clean_name}.X")
    os.makedirs(os.path.join(project_dir, "nbproject"), exist_ok=True)

    # Template source: use traffic_controller.X or digital_lock.X as reliable template
    template_dir = os.path.join(PROJECTS_DIR, "traffic_controller.X")
    if not os.path.exists(template_dir):
        template_dir = os.path.join(PROJECTS_DIR, "digital_lock.X")

    if os.path.exists(template_dir):
        template_base = os.path.basename(template_dir).replace(".X", "")
        
        # Copy root Makefile
        src_mf = os.path.join(template_dir, "Makefile")
        if os.path.exists(src_mf):
            shutil.copy2(src_mf, os.path.join(project_dir, "Makefile"))

        # Copy entire nbproject directory
        src_nb = os.path.join(template_dir, "nbproject")
        dst_nb = os.path.join(project_dir, "nbproject")
        if os.path.exists(dst_nb):
            shutil.rmtree(dst_nb)
        shutil.copytree(src_nb, dst_nb)

        # Patch all text files in nbproject
        for root, _, files in os.walk(dst_nb):
            for file in files:
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as rf:
                        content = rf.read()
                    content = content.replace(template_base, clean_name)
                    with open(fpath, "w", encoding="utf-8") as wf:
                        wf.write(content)
                except Exception:
                    pass


    # Ensure standard headers and configuration bits are properly ordered at the top
    headers_and_pragmas = (
        "#include <xc.h>\n"
        "#include <stdio.h>\n"
        "#include <stdint.h>\n"
        "#include <stdbool.h>\n\n"
        "// Configuration Fuses for PIC18F85K22\n"
        "#pragma config XINST   = OFF      // Extended Instruction Set disabled (Mandatory for XC8)\n"
        "#pragma config FOSC    = HS1      // High-Speed Crystal (4.9152 MHz)\n"
        "#pragma config SOSCSEL = DIG      // Digital mode on RC0/RC1\n"
        "#pragma config WDTEN   = OFF      // Watchdog Timer disabled\n"
        "#pragma config BOREN   = ON       // Brown-out Reset enabled\n"
        "#pragma config PWRTEN  = ON       // Power-up Timer enabled\n\n"
        "#define _XTAL_FREQ 4915200UL      // 4.9152 MHz crystal\n\n"
    )

    # If code uses 4-bit nibble or flawed LATD LCD driver, replace with verified 8-bit PORTH driver
    if "LCD_Nibble" in c_source_code or "LCD_D4" in c_source_code or ("LCD" in c_source_code and "LATH" not in c_source_code):
        # Strip existing headers and pragma lines from user code to prevent duplicate / conflict
        c_source_code = re.sub(r'#include\s*<[^>]+>\s*\n?', '', c_source_code)
        c_source_code = re.sub(r'#pragma\s+config[^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+_XTAL_FREQ[^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+LCD_DATA[^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+LCD_D[4-7][^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+LCD_RS[^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+LCD_EN[^\n]*\n?', '', c_source_code)
        c_source_code = re.sub(r'#define\s+LCD_BACKLIGHT[^\n]*\n?', '', c_source_code)
        
        # Helper to cleanly remove C functions even with nested while/for/if loops
        def _strip_function(src, func_name):
            pattern = re.compile(r'\b(?:void|char|int|uint8_t)\s+' + re.escape(func_name) + r'\s*\([^)]*\)\s*\{')
            while True:
                m = pattern.search(src)
                if not m:
                    break
                start = m.start()
                brace_count = 0
                end = -1
                for i in range(m.end() - 1, len(src)):
                    if src[i] == '{':
                        brace_count += 1
                    elif src[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                if end != -1:
                    src = src[:start] + src[end:]
                else:
                    break
            return src

        for fn in ["LCD_Pulse_Enable", "LCD_Nibble", "LCD_Cmd", "LCD_Command", "LCD_Data", "LCD_Char", "LCD_String", "LCD_Set_Cursor", "LCD_Clear", "initLCD", "LCD_Init"]:
            c_source_code = _strip_function(c_source_code, fn)

        # Fix buzzer / piezo if RA4 was wrongly assigned to piezo instead of LCD backlight
        c_source_code = re.sub(r'TRISA4\s*=\s*0;?', 'TRISAbits.TRISA5 = 0; // Buzzer on RA5', c_source_code)
        c_source_code = re.sub(r'LATA4\s*=\s*1;?', 'LATAbits.LATA5 = 1;', c_source_code)
        c_source_code = re.sub(r'LATA4\s*=\s*0;?', 'LATAbits.LATA5 = 0;', c_source_code)

        verified_lcd = """// --- HARDWARE 16x2 LCD DRIVER (8-BIT ON PORTH) ---
#define LCD_DATA_LAT   LATH
#define LCD_DATA_TRIS  TRISH
#define LCD_RS_LAT     LATEbits.LATE0
#define LCD_RS_TRIS    TRISEbits.TRISE0
#define LCD_EN_LAT     LATEbits.LATE1
#define LCD_EN_TRIS    TRISEbits.TRISE1
#define LCD_BL_LAT     LATAbits.LATA4
#define LCD_BL_TRIS    TRISAbits.TRISA4

void LCD_Pulse_Enable(void) {
    LCD_EN_LAT = 1;
    __delay_us(25);
    LCD_EN_LAT = 0;
    __delay_us(25);
}

void LCD_Command(unsigned char cmd) {
    LCD_RS_LAT = 0;
    LCD_DATA_LAT = cmd;
    __delay_us(5);
    LCD_Pulse_Enable();
    if (cmd == 0x01 || cmd == 0x02) {
        __delay_ms(3);
    } else {
        __delay_us(80);
    }
}

void LCD_Cmd(unsigned char cmd) { LCD_Command(cmd); }

void LCD_Char(char data) {
    LCD_RS_LAT = 1;
    LCD_DATA_LAT = (unsigned char)data;
    __delay_us(5);
    LCD_Pulse_Enable();
    __delay_us(60);
}

void LCD_Data(unsigned char d) { LCD_Char((char)d); }

void LCD_String(const char *str) {
    while (*str) {
        LCD_Char(*str++);
    }
}

void LCD_Set_Cursor(unsigned char row, unsigned char col) {
    LCD_Command(0xC0 + (col - 1)); // Always Line 2 (0xC0) on this trainer
}

void LCD_Clear(void) {
    LCD_Command(0x01);
}

void LCD_Init(void) {
    __delay_ms(100);
    LCD_BL_TRIS = 0;
    LCD_BL_LAT  = 0; // Turn ON Backlight (Active Low)

    LCD_DATA_TRIS = 0x00; // PORTH = Output
    LCD_RS_TRIS   = 0;    // RE0 = Output
    LCD_EN_TRIS   = 0;    // RE1 = Output

    LCD_Command(0x30); __delay_ms(10);
    LCD_Command(0x30); __delay_ms(2);
    LCD_Command(0x30); __delay_us(200);

    LCD_Command(0x38); __delay_us(100); // 8-bit, 2 lines, 5x8
    LCD_Command(0x08); __delay_us(100); // Display OFF
    LCD_Command(0x01); __delay_ms(3);   // Clear
    LCD_Command(0x06); __delay_us(100); // Auto increment
    LCD_Command(0x0C); __delay_ms(2);   // Display ON, cursor off
}
void initLCD(void) { LCD_Init(); }
"""
        c_source_code = headers_and_pragmas + verified_lcd + "\n" + c_source_code.strip()
    else:
        # Standard healing for missing pragmas / headers
        if "XINST" not in c_source_code:
            c_source_code = headers_and_pragmas + c_source_code
        elif "_XTAL_FREQ" not in c_source_code:
            c_source_code = "#define _XTAL_FREQ 4915200UL\n" + c_source_code

    # Write the C source code
    c_file_path = os.path.join(project_dir, f"{clean_name}.c")
    with open(c_file_path, "w", encoding="utf-8") as f:
        f.write(c_source_code)

    # Compile with make.exe
    build_res = compile_project(clean_name)


    return {
        "project_name": clean_name,
        "project_dir": project_dir,
        "c_file": c_file_path,
        "audit": audit,
        "build": build_res
    }

