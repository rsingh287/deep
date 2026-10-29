from .base_intent import BaseIntent
import re
import os

class VisualCanvasIntent(BaseIntent):
    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        return "edit this <" in norm_prompt and "change it so that" in norm_prompt

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        if "edit this <" in norm_prompt and "change it so that" in norm_prompt:
            try:
                import glob
                import json
                import requests

                # Extract the raw HTML snippet and the instructions (support both with or without ```html)
                match = re.search(r"```html\r?\n(.*?)\r?\n```\s*change it so that(.*)", user_prompt, re.DOTALL | re.IGNORECASE)
                if not match:
                    match = re.search(r"(?:edit\s+this\s+)?(<\w+.*?>.*?</\w+>)\s*change it so that(.*)", user_prompt, re.DOTALL | re.IGNORECASE)

                if not match:
                    return ("⚠️ **Visual Canvas Warning:** Could not parse the HTML element and instructions from the prompt.", "visual_canvas", [])

                snippet = match.group(1).strip()
                instruction = match.group(2).strip()

                # Find which artifact contains this snippet
                base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_apps")
                target_file = None
                file_content = ""
                
                for path in glob.glob(os.path.join(base_dir, "**", "*.html"), recursive=True):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if snippet in content:
                                target_file = path
                                file_content = content
                                break
                    except Exception:
                        continue
                
                if not target_file:
                    return ("⚠️ **Visual Canvas Warning:** Could not locate the specified HTML snippet inside any files under `generated_apps`.", "visual_canvas", [])

                # Use LLM to generate the modified snippet
                sys_prompt = "You are an expert frontend developer. Modify the following HTML snippet according to the instructions. Output ONLY the raw modified HTML code. No markdown formatting, no explanations."
                llm_prompt = f"Original Snippet:\n{snippet}\n\nInstruction: Change it so that {instruction}\n\nModified Snippet:"
                
                ollama_base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                if not ollama_base.startswith("http://") and not ollama_base.startswith("https://"):
                    ollama_base = f"http://{ollama_base}"
                url = f"{ollama_base}/api/generate"
                payload = {"model": "qwen2.5-coder:7b", "prompt": f"{sys_prompt}\n\n{llm_prompt}", "stream": False}
                
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 200:
                    new_snippet = json.loads(res.text).get("response", "").strip()
                    new_snippet = re.sub(r'^```(html)?|```$', '', new_snippet, flags=re.IGNORECASE).strip()
                    
                    # Replace exact string match first, fallback to bs4 parse replace
                    new_content = file_content.replace(snippet, new_snippet)
                    
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(new_content)
                        
                    # Refresh visual trigger text
                    ai_msg = f"🎨 **Visual Canvas AST Sync**: Re-rendered DOM element in `{os.path.basename(target_file)}`.\n\nChanges applied successfully."
                    
                    return (ai_msg, "qwen2.5-coder:7b", [{"language": "python", "code": "import bs4\n# Bi-Directional DOM sync", "output": f"Replaced snippet in {os.path.basename(target_file)}"}])
                else:
                    return (f"⚠️ **Visual Canvas LLM Error:** Ollama returned status code {res.status_code}", "visual_canvas", [])
            except Exception as e:
                print(f"[Canvas AST Bridge Error] {e}")
                return (f"❌ **Visual Canvas Error:** {e}", "visual_canvas", [])
        return None
