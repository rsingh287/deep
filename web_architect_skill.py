import http.server
import json
import os
import re
import socket
import socketserver
import threading

import requests


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def serve_directory(directory, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()


def generate_html_with_ollama(topic):
    system_prompt = (
        "You are an expert full-stack web designer. The user wants a modern, fully-styled website for mobile phones and desktop. "
        "Generate a complete, beautiful single-file HTML5 page with modern CSS (flexbox, CSS grid, media queries, smooth animations, dark futuristic theme) and interactive JavaScript. "
        "Return ONLY the complete raw HTML code starting with <!DOCTYPE html> and ending with </html>. "
        "Do not include explanation text or markdown codeblocks."
    )

    prompt = f"Topic: {topic}\nBuild the complete single-file HTML website with embedded CSS and JavaScript now:"

    url = "http://127.0.0.1:11434/api/generate"
    models_to_try = ["qwen2.5-coder:7b", "qwen2.5:3b", "qwen2.5:7b"]

    for model_name in models_to_try:
        payload = {"model": model_name, "prompt": prompt, "system": system_prompt, "stream": False}
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                res_data = json.loads(response.text)
                text = res_data.get("response", "").strip()
                
                # Check for refusal
                if any(ref in text.lower() for ref in ["can't fulfill", "cannot fulfill", "as an ai", "i cannot"]):
                    continue

                html_match = re.search(r'(<!DOCTYPE html.*?>.*?</html>|<html.*?>.*?</html>)', text, re.IGNORECASE | re.DOTALL)
                if html_match:
                    return html_match.group(1).strip()

                text = re.sub(r'^```(?:html)?\s*', '', text, flags=re.IGNORECASE)
                text = re.sub(r'\s*```$', '', text)
                if "<html" in text.lower() and "</html>" in text.lower():
                    return text.strip()
        except Exception as e:
            print(f"[WebArchitect] Error calling {model_name}: {e}")

    # Fallback high-tech template
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{topic}</title>
<style>
  :root {{ --bg: #090d16; --card: #111827; --primary: #00f0ff; --accent: #10b981; --text: #f3f4f6; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
  body {{ background: var(--bg); color: var(--text); padding: 20px; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .phone-card {{ width: 100%; max-width: 420px; background: var(--card); border: 1px solid rgba(0,240,255,0.25); border-radius: 28px; padding: 28px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
  h1 {{ font-size: 1.6rem; color: var(--primary); margin-bottom: 12px; }}
  p {{ color: #9ca3af; line-height: 1.6; margin-bottom: 20px; font-size: 0.95rem; }}
  .badge {{ display: inline-block; padding: 4px 12px; background: rgba(0,240,255,0.15); color: var(--primary); border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 16px; }}
  .action-btn {{ display: block; width: 100%; padding: 14px; background: linear-gradient(135deg, #00f0ff, #0284c7); border: none; border-radius: 14px; color: #000; font-weight: bold; font-size: 1rem; cursor: pointer; text-align: center; text-decoration: none; }}
</style>
</head>
<body>
  <div class="phone-card">
    <div class="badge">TACTICAL SYSTEM ONLINE</div>
    <h1>{topic}</h1>
    <p>Mobile interface loaded successfully under the command of J.A.R.V.I.S. & F.R.I.D.A.Y.</p>
    <a href="#" class="action-btn" onclick="alert('System operational!')">Initialize Interface</a>
  </div>
</body>
</html>"""


def build_premium_website(project_name, topic):
    base_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "generated_apps", project_name
    )
    os.makedirs(base_dir, exist_ok=True)

    index_path = os.path.join(base_dir, "index.html")

    html_content = generate_html_with_ollama(topic)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    main_server_url = f"http://127.0.0.1:5000/generated_apps/{project_name}/index.html"
    port = get_free_port()
    live_url = f"http://127.0.0.1:{port}"

    meta_path = os.path.join(base_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"project": project_name, "topic": topic, "url": live_url, "permanent_url": main_server_url}, f, indent=4)

    # Start server in a background thread
    server_thread = threading.Thread(
        target=serve_directory, args=(base_dir, port), daemon=True
    )
    server_thread.start()

    return f"Deployed successfully to {main_server_url} (Standalone: {live_url}) | Path: {index_path}"
