from flask import Blueprint
from flask_sock import Sock
import threading
import json
import os

try:
    from winpty import PtyProcess
    HAS_WINPTY = True
except ImportError:
    HAS_WINPTY = False

pty_bp = Blueprint("pty", __name__)
sock = Sock()

PTYS = {}

@sock.route("/api/terminal")
def terminal_socket(ws):
    if not HAS_WINPTY:
        ws.send(json.dumps({"type": "output", "data": "Error: winpty is not installed. Run 'pip install pywinpty' on Windows.\\r\\n"}))
        return
        
    term_id = os.urandom(4).hex()
    
    # Spawn powershell inside ConPTY
    # Dimensions can be updated later
    proc = PtyProcess.spawn("powershell.exe", dimensions=(24, 80))
    PTYS[term_id] = proc
    
    # Read thread
    def read_output():
        while proc.isalive():
            try:
                data = proc.read(1024)
                if data:
                    ws.send(json.dumps({"type": "output", "data": data}))
            except EOFError:
                break
            except Exception as e:
                print(f"PTY read error: {e}")
                break
        try:
            ws.send(json.dumps({"type": "output", "data": "\\r\\n[Process Exited]\\r\\n"}))
            ws.close()
        except:
            pass
            
    threading.Thread(target=read_output, daemon=True).start()
    
    # Write loop
    while True:
        try:
            msg = ws.receive()
            if msg is None:
                break
            data = json.loads(msg)
            if data["type"] == "input":
                proc.write(data["data"])
            elif data["type"] == "resize":
                proc.setwinsize(data["rows"], data["cols"])
        except Exception as e:
            print(f"WS error: {e}")
            break
            
    if proc.isalive():
        proc.terminate()
    if term_id in PTYS:
        del PTYS[term_id]
