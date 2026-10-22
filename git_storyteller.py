import subprocess
import os

def generate_git_changelog(repo_path="."):
    print(f"[GitStoryteller] Parsing Git history for {repo_path}...")
    try:
        # Get today's commits
        cmd = 'git log --since="midnight" --pretty=format:"%h - %s (%an)"'
        res = subprocess.run(cmd, shell=True, cwd=repo_path, capture_output=True, text=True)
        
        commits = res.stdout.strip()
        if not commits:
            return {"status": "success", "changelog": "No commits found today."}
            
        changelog = "# 🚀 Executive Daily Changelog\n\n"
        changelog += "## 🔧 Commits\n"
        for line in commits.split('\n'):
            changelog += f"- {line}\n"
            
        changelog += "\n## 📊 Summary\n"
        changelog += "Architectural refactors and daily fixes successfully committed to the repository."
        
        return {"status": "success", "changelog": changelog}
    except Exception as e:
        return {"status": "error", "message": str(e)}
