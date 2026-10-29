"""
==============================================================================
D.E.E.P Sovereign AI PC Cockpit - Embedded MCU Engine (PIC18F85K22 & PICkit 3)
==============================================================================
Provides automated 1-click compilation, pre-flash static audit, and USB-safe
flashing for the Microchip PIC18F Trainer 2 (PIC18F85K22) using xc8-cc and ipecmd.
"""

import os
import subprocess
import threading
import time
from typing import Dict, Any, List, Optional
import code_scanner_engine

# Toolchain Default Paths
XC8_BIN = r"C:\Program Files\Microchip\xc8\v3.10\bin\xc8-cc.exe"
IPECMD_BIN = r"C:\Program Files\Microchip\MPLABX\v6.30\mplab_platform\mplab_ipe\ipecmd.exe"
PROJECTS_DIR = r"C:\Users\User\MPLABXProjects"

# Hardware Profile Constants (from AGENTS.md)
TARGET_MCU = "18F85K22"
PROGRAMMER_TYPE = "PK3"
PROGRAMMER_SERIAL = "BUR181916585"
XTAL_FREQ = 4915200
DFP_DIR = r"C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8"

# Mutex to ensure only one process talks to PICkit 3 over USB
PICKIT3_USB_MUTEX = threading.Lock()


def get_toolchain_status() -> Dict[str, Any]:
    """Returns detected status of xc8-cc, ipecmd, and MPLABX projects."""
    xc8_found = os.path.isfile(XC8_BIN)
    ipecmd_found = os.path.isfile(IPECMD_BIN)
    
    projects = []
    if os.path.exists(PROJECTS_DIR):
        for entry in os.listdir(PROJECTS_DIR):
            proj_path = os.path.join(PROJECTS_DIR, entry)
            if os.path.isdir(proj_path) and entry.endswith(".X"):
                # Check for main C file and hex file
                c_files = [f for f in os.listdir(proj_path) if f.endswith(".c")]
                hex_files = []
                for root, _, files in os.walk(proj_path):
                    for f in files:
                        if f.endswith(".hex"):
                            hex_files.append(os.path.relpath(os.path.join(root, f), proj_path))
                
                projects.append({
                    "name": entry,
                    "path": proj_path,
                    "c_files": c_files,
                    "hex_files": hex_files
                })

    return {
        "success": True,
        "target_mcu": TARGET_MCU,
        "programmer": f"PICkit 3 ({PROGRAMMER_SERIAL})",
        "xc8_available": xc8_found,
        "xc8_path": XC8_BIN if xc8_found else None,
        "ipecmd_available": ipecmd_found,
        "ipecmd_path": IPECMD_BIN if ipecmd_found else None,
        "projects_count": len(projects),
        "projects": projects
    }


def audit_project_firmware(project_name: str) -> Dict[str, Any]:
    """Runs pre-flash static analysis on C source files in the project."""
    proj_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.isdir(proj_path):
        return {"success": False, "error": f"Project directory not found: {proj_path}"}

    c_files = [os.path.join(proj_path, f) for f in os.listdir(proj_path) if f.endswith(".c")]
    if not c_files:
        return {"success": False, "error": f"No .c files found in project {project_name}"}

    all_findings = []
    for c_file in c_files:
        rel = os.path.basename(c_file)
        findings = code_scanner_engine.scan_embedded_c_file(c_file, rel)
        if findings:
            all_findings.extend(findings)

    passed = len(all_findings) == 0
    return {
        "success": True,
        "project": project_name,
        "passed": passed,
        "findings": all_findings,
        "message": "All hardware directives passed!" if passed else f"Found {len(all_findings)} hardware directive warning(s)."
    }


def compile_project(project_name: str) -> Dict[str, Any]:
    """Compiles C source code into a HEX file using xc8-cc."""
    if not os.path.isfile(XC8_BIN):
        return {"success": False, "error": f"xc8-cc compiler not found at {XC8_BIN}"}

    proj_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.isdir(proj_path):
        return {"success": False, "error": f"Project not found: {project_name}"}

    c_files = [f for f in os.listdir(proj_path) if f.endswith(".c")]
    if not c_files:
        return {"success": False, "error": f"No C files in {project_name}"}

    main_c = os.path.join(proj_path, c_files[0])
    out_hex = os.path.join(proj_path, f"{project_name.replace('.X', '')}.hex")

    # Command: xc8-cc -mcpu=18F85K22 -mdfp=<dfp_dir> -O2 -o <out_hex> <source.c>
    cmd = [
        XC8_BIN,
        f"-mcpu={TARGET_MCU}",
        f"-mdfp={DFP_DIR}",
        "-O2",
        f"-o{out_hex}",
        main_c
    ]

    start_time = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        elapsed = round(time.time() - start_time, 2)
        
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")
        success = proc.returncode == 0 and os.path.isfile(out_hex)

        return {
            "success": success,
            "project": project_name,
            "elapsed_seconds": elapsed,
            "hex_path": out_hex if success else None,
            "hex_size_bytes": os.path.getsize(out_hex) if success else 0,
            "output": output.strip(),
            "returncode": proc.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Compilation timed out after 30 seconds."}
    except Exception as e:
        return {"success": False, "error": f"Compilation failed: {str(e)}"}


def flash_project(project_name: str, hex_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Flashes target PIC18F85K22 over USB using PICkit 3 (BUR181916585) via ipecmd.
    Uses strict USB mutex to prevent concurrent driver lockouts.
    """
    if not os.path.isfile(IPECMD_BIN):
        return {"success": False, "error": f"ipecmd not found at {IPECMD_BIN}"}

    proj_path = os.path.join(PROJECTS_DIR, project_name)
    if not hex_path:
        # Search for .hex file in project
        target_hex = None
        for root, _, files in os.walk(proj_path):
            for f in files:
                if f.endswith(".hex"):
                    target_hex = os.path.join(root, f)
                    break
            if target_hex:
                break
        hex_path = target_hex

    if not hex_path or not os.path.isfile(hex_path):
        return {"success": False, "error": f"No compiled HEX file found for {project_name}. Please compile first."}

    # Pre-flash static audit check
    audit = audit_project_firmware(project_name)
    if not audit.get("passed", False):
        return {
            "success": False,
            "error": "Pre-flash hardware audit rejected this firmware. Fix hardware rule violations before flashing.",
            "audit_findings": audit.get("findings", [])
        }

    # Acquire PICkit 3 USB mutex
    acquired = PICKIT3_USB_MUTEX.acquire(blocking=False)
    if not acquired:
        return {
            "success": False,
            "error": "PICkit 3 USB hardware is currently busy in another flashing session. Please wait."
        }

    try:
        # Command per AGENTS.md:
        # ipecmd.exe -P18F85K22 -TPPK3 -TSBUR181916585 -M -F"<path_to_hex>" -OL
        cmd = [
            IPECMD_BIN,
            f"-P{TARGET_MCU}",
            f"-TP{PROGRAMMER_TYPE}",
            f"-TS{PROGRAMMER_SERIAL}",
            "-M",
            f"-F{hex_path}",
            "-OL"
        ]

        start_time = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        elapsed = round(time.time() - start_time, 2)
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")

        # Check for Device ID (00000000) power alert
        device_id_alert = "00000000" in output or "Target Device ID (0x0)" in output
        success = ("Programming/Verify complete" in output or "Program Succeeded" in output) and not device_id_alert

        return {
            "success": success,
            "project": project_name,
            "hex_path": hex_path,
            "elapsed_seconds": elapsed,
            "device_id_alert": device_id_alert,
            "device_id_message": "Alert: Target Device ID is 0x00000000. Verify the 5V/9V DC power supply on the PIC18F Trainer board!" if device_id_alert else None,
            "output": output.strip(),
            "returncode": proc.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Flashing timed out after 45 seconds."}
    except Exception as e:
        return {"success": False, "error": f"Flashing execution error: {str(e)}"}
    finally:
        PICKIT3_USB_MUTEX.release()
