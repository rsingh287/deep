import re
import subprocess
import urllib.parse
import webbrowser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AntigravityAI-PublicEngine/1.0"
}

W3_TOPIC_MAP = {
    "html": "https://www.w3schools.com/html/",
    "css": "https://www.w3schools.com/css/",
    "javascript": "https://www.w3schools.com/js/",
    "js": "https://www.w3schools.com/js/",
    "python": "https://www.w3schools.com/python/",
    "sql": "https://www.w3schools.com/sql/",
    "java": "https://www.w3schools.com/java/",
    "cpp": "https://www.w3schools.com/cpp/",
    "c++": "https://www.w3schools.com/cpp/",
    "c#": "https://www.w3schools.com/cs/",
    "cs": "https://www.w3schools.com/cs/",
    "react": "https://www.w3schools.com/react/",
    "php": "https://www.w3schools.com/php/",
    "bootstrap": "https://www.w3schools.com/bootstrap5/",
    "jquery": "https://www.w3schools.com/jquery/",
    "git": "https://www.w3schools.com/git/",
    "django": "https://www.w3schools.com/django/",
    "typescript": "https://www.w3schools.com/typescript/",
    "ts": "https://www.w3schools.com/typescript/",
    "r": "https://www.w3schools.com/r/",
    "kotlin": "https://www.w3schools.com/kotlin/",
    "go": "https://www.w3schools.com/go/",
    "node": "https://www.w3schools.com/nodejs/",
    "nodejs": "https://www.w3schools.com/nodejs/",
    "mongodb": "https://www.w3schools.com/mongodb/",
    "mysql": "https://www.w3schools.com/mysql/",
}


def handle_w3schools_intent(prompt: str):
    p_low = prompt.lower().strip()

    triggers = [
        "w3schools",
        "w3school",
        "w3 school",
        "w3schools tutorial",
        "w3schools search",
        "w3 tutorial",
    ]
    if not any(k in p_low for k in triggers):
        return None

    # Clean query
    clean_q = re.sub(
        r"^(w3schools|w3school|w3 school|w3schools search|w3 tutorial|w3schools tutorial|search w3schools|search w3)\s+",
        "",
        p_low,
        flags=re.IGNORECASE,
    ).strip()
    clean_q = re.sub(
        r"\b(for|on|about|tutorial|tutorials|docs|reference)\b",
        "",
        clean_q,
        flags=re.IGNORECASE,
    ).strip()

    if not clean_q:
        clean_q = "html"

    # Direct Topic Match or Custom Search
    if clean_q in W3_TOPIC_MAP:
        target_url = W3_TOPIC_MAP[clean_q]
        topic_name = clean_q.upper()
    else:
        target_url = f"https://www.google.com/search?q=site%3Aw3schools.com+{urllib.parse.quote(clean_q)}"
        topic_name = clean_q.title()

    # Open W3Schools in Google Chrome
    try:
        subprocess.Popen(
            [r"C:\Program Files\Google\Chrome\Application\chrome.exe", target_url]
        )
    except Exception:
        webbrowser.open(target_url)

    return (
        f"Opened W3Schools tutorial for '{topic_name}' in Google Chrome.",
        "autonomous_w3schools_search_engine",
        [
            {
                "language": "powershell",
                "code": f"start chrome '{target_url}'",
                "output": f"Opened W3Schools Tutorial for '{topic_name}'",
            }
        ],
    )
