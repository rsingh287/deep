import os
import subprocess
import requests

def take_pre_execution_snapshot(reason="Workstation command execution"):
    """Creates a lightweight snapshot commit before autonomous code execution so the user can easily undo/revert."""
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        if status:
            subprocess.check_call(["git", "add", "-A"])
            msg = f"Auto-Snapshot: {reason[:45].strip()}"
            subprocess.check_call(["git", "commit", "-m", msg])
            return True
    except Exception as e:
        print(f"[GitAutopilot Snapshot] Notice: {e}")
    return False

def handle_git_intent(user_prompt: str):
    prompt_low = user_prompt.lower().strip()
    
    triggers = [
        "undo", "revert", "rollback", "go back", "git reset", "git checkout",
        "restore workspace", "discard changes", "undo my last mess"
    ]
    if not any(t in prompt_low for t in triggers):
        return None
        
    try:
        # First check git status for uncommitted or newly created files
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        if status:
            # Revert modified files and remove newly generated untracked files
            subprocess.check_call(["git", "reset", "--hard"])
            subprocess.check_call(["git", "clean", "-fd"])
            return (
                "🔄 **Git Autopilot & Workspace Rollback:** Detected uncommitted modifications and newly generated files. I have performed a clean reset to restore your workspace to the last clean checkpoint.",
                "git_autopilot",
                [
                    {"language": "powershell", "code": "git reset --hard", "output": "Restored modified files to HEAD"},
                    {"language": "powershell", "code": "git clean -fd", "output": "Removed newly generated untracked files"}
                ]
            )
        
        # If working directory is clean, check if we can revert the last commit
        commit_count = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], text=True).strip())
        if commit_count > 1:
            last_commit = subprocess.check_output(["git", "log", "-1", "--oneline"], text=True).strip()
            subprocess.check_call(["git", "reset", "--hard", "HEAD~1"])
            return (
                f"🔄 **Git Autopilot & Workspace Rollback:** Reverted commit (`{last_commit}`). Your workspace has been successfully rolled back to the previous snapshot state.",
                "git_autopilot",
                [{"language": "powershell", "code": "git reset --hard HEAD~1", "output": f"Rolled back {last_commit}"}]
            )
        else:
            return (
                "🔄 **Git Autopilot:** Workspace is already in a clean baseline state. No further actions to roll back.",
                "git_autopilot",
                [{"language": "powershell", "code": "git status", "output": "Workspace is clean and up to date"}]
            )
    except Exception as e:
        return (f"❌ **Git Autopilot Error:** Failed to restore workspace: {e}", "git_autopilot", [])
