import subprocess
import os

def run_code_cleaner(directory_path: str) -> str:
    """Runs autoflake, isort, and black on the specified directory."""
    target_dir = directory_path.strip().strip("\"'")
    
    if not target_dir or not os.path.exists(target_dir):
        return f"Error: The directory '{target_dir}' does not exist. Please provide a valid path."
        
    results = []
    
    try:
        # 1. Run autoflake
        autoflake_cmd = ["autoflake", "--in-place", "--remove-all-unused-imports", "--remove-unused-variables", "-r", target_dir]
        subprocess.run(autoflake_cmd, check=True, capture_output=True, text=True)
        results.append("✅ Autoflake: Successfully removed unused imports and variables.")
        
        # 2. Run isort
        isort_cmd = ["isort", target_dir]
        subprocess.run(isort_cmd, check=True, capture_output=True, text=True)
        results.append("✅ Isort: Successfully sorted and organized all imports.")
        
        # 3. Run black
        black_cmd = ["black", target_dir]
        black_result = subprocess.run(black_cmd, capture_output=True, text=True)
        # Black outputs to stderr even on success
        output_msg = black_result.stderr.strip().split('\n')[-1]
        results.append(f"✅ Black: Reformatted code to PEP-8 standards. ({output_msg})")
        
        return "Code Cleanup Complete!\n\n" + "\n".join(results)
        
    except subprocess.CalledProcessError as e:
        return f"Error running cleanup tools:\nCommand: {' '.join(e.cmd)}\nError: {e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
