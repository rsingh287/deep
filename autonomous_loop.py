import threading
import time

from agentic_orchestrator import orchestrator


class AutonomousEnterpriseLoop:
    def __init__(self, interval_seconds=300):
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None
        self.autonomous_goals = [
            "system audit and optimize",
            "predict future trends",
            "run quant forecast",
            "heal and optimize",
        ]
        self.goal_index = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(
            f"[AutonomousLoop] Enterprise background daemon started. Interval: {self.interval_seconds}s"
        )

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        print("[AutonomousLoop] Enterprise background daemon stopped.")

    def _loop(self):
        while self.running:
            try:
                # Rotate through goals
                current_goal = self.autonomous_goals[self.goal_index]
                self.goal_index = (self.goal_index + 1) % len(self.autonomous_goals)

                print(
                    f"[AutonomousLoop] Triggering autonomous execution for goal: {current_goal}"
                )

                # We turn off voice synthesis for background tasks so it doesn't randomly speak
                result = orchestrator.plan_and_execute(goal=current_goal, speak=False)

                print(
                    f"[AutonomousLoop] Execution completed. Verdict: {result.get('verdict', 'N/A')}"
                )

            except Exception as e:
                print(f"[AutonomousLoop] Error in background execution: {e}")

            time.sleep(self.interval_seconds)


# Singleton instance
enterprise_loop = AutonomousEnterpriseLoop(interval_seconds=600)  # Every 10 mins

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("Starting standalone autonomous loop test...")
    enterprise_loop.interval_seconds = 10  # 10s for testing
    enterprise_loop.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        enterprise_loop.stop()
