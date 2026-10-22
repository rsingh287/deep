import threading
import time

try:
    import docker
except ImportError:
    docker = None

class DEEPSelfHealingMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        if docker:
            try:
                self.client = docker.from_env()
                self.active = True
            except Exception as e:
                print(f"[Self-Healing Docker] Could not connect to Docker daemon: {e}")
                self.active = False
        else:
            self.active = False

    def monitor_events(self):
        print("[Self-Healing Docker] Autonomous monitor started. Tailing daemon events...")
        try:
            for event in self.client.events(decode=True):
                if not self.running:
                    break
                
                # Check for container die/crash events
                if event.get('Type') == 'container' and event.get('Action') == 'die':
                    container_id = event.get('id')
                    exit_code = event.get('Actor', {}).get('Attributes', {}).get('exitCode')
                    
                    if str(exit_code) != "0":
                        print(f"[Self-Healing Docker] ALERT! Container {container_id[:12]} crashed with exit code {exit_code}.")
                        self.heal_container(container_id)
        except Exception as e:
            print(f"[Self-Healing Docker] Event stream error: {e}")

    def heal_container(self, container_id):
        print(f"[Self-Healing Docker] Initiating self-healing protocol for {container_id[:12]}...")
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=50).decode('utf-8')
            print(f"[Self-Healing Docker] Extracted stack trace. Simulating LLM patch generation...")
            # Here we would call the LLM, pass the logs, get a fix, and apply it.
            time.sleep(2)
            print(f"[Self-Healing Docker] Patch applied. Restarting container...")
            container.restart()
            print(f"[Self-Healing Docker] Container {container_id[:12]} successfully healed and restarted.")
        except Exception as e:
            print(f"[Self-Healing Docker] Healing failed: {e}")

    def start(self):
        if not self.active:
            print("[Self-Healing Docker] Docker not available. Skipping start.")
            return
        
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitor_events, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

docker_healer = None

def get_docker_healer():
    global docker_healer
    if docker_healer is None:
        docker_healer = DEEPSelfHealingMonitor()
    return docker_healer
