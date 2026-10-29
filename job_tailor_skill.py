import json
import os
import urllib.parse
import ipaddress

import requests
from bs4 import BeautifulSoup

from advanced_document_exporter import export_document


def _is_safe_url(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = (parsed.hostname or "").strip().lower()
        if not hostname:
            return False
        if hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0", "169.254.169.254"):
            return False
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            pass
        return True
    except Exception:
        return False


def run_job_tailor(job_url: str, resume_text: str) -> str:
    """Scrapes a job posting and uses Ollama to rewrite the resume text to match."""
    # 1. Scrape the URL
    if not _is_safe_url(job_url):
        return "Failed to scrape job URL: Invalid or restricted URL target (SSRF prevention)."

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(job_url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        job_description = soup.get_text(separator=" ", strip=True)[:5000]  # Cap length
    except Exception as e:
        return f"Failed to scrape job URL: {e}"

    # 2. Call Ollama
    url = "http://localhost:11434/api/generate"
    system = (
        "You are an expert Resume Tailoring AI. "
        "The user will provide their CURRENT RESUME and a JOB DESCRIPTION. "
        "You must rewrite the resume to highlight skills and experiences that match the job description. "
        "You must output ONLY valid JSON with no extra markdown text. "
        "The JSON format should be: "
        '{"title": "Tailored_Resume", "paragraphs": ["paragraph 1", "paragraph 2", ...] }'
    )

    prompt = f"CURRENT RESUME:\n{resume_text}\n\nJOB DESCRIPTION:\n{job_description}"

    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "system": system,
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        doc_data = json.loads(data.get("response", "{}"))

        title = doc_data.get("title", "Tailored_Resume")
        paragraphs = doc_data.get("paragraphs", [])

        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "generated_apps",
            "deep_workspace",
        )
        res = export_document(title, paragraphs, output_dir)
        files = res.get("files", []) if isinstance(res, dict) else []

        return f"Successfully tailored resume to job! Saved in formats: {', '.join(files)}"
    except Exception as e:
        return f"Failed to tailor resume: {e}"

