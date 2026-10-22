import json
import os

import requests
from bs4 import BeautifulSoup

from advanced_document_exporter import export_document


def run_job_tailor(job_url: str, resume_text: str) -> str:
    """Scrapes a job posting and uses Ollama to rewrite the resume text to match."""
    # 1. Scrape the URL
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(job_url, headers=headers, timeout=15)
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

        return f"Successfully tailored resume to job! Saved in formats: {', '.join(res.get('files', []))}"
    except Exception as e:
        return f"Failed to tailor resume: {e}"
