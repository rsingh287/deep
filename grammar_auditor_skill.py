import json
import os

import requests

from advanced_document_exporter import export_document


def run_grammar_auditor(document_text: str) -> str:
    """Uses Ollama to audit and improve the grammar, tone, and readability of a document."""
    url = "http://localhost:11434/api/generate"
    system = (
        "You are an expert Document Editor and Grammar Auditor. "
        "The user will provide the text of a document. "
        "You must improve the grammar, rewrite passive voice to active voice, "
        "and improve the readability and impact (especially for resumes). "
        "You must output ONLY valid JSON with no extra markdown text. "
        "The JSON format should be: "
        '{"title": "Audited_Document", "paragraphs": ["paragraph 1", "paragraph 2", ...] }'
    )

    payload = {
        "model": "qwen2.5:7b",
        "prompt": document_text,
        "system": system,
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        data = response.json()
        doc_data = json.loads(data.get("response", "{}"))

        title = doc_data.get("title", "Audited_Document")
        paragraphs = doc_data.get("paragraphs", [])

        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "generated_apps",
            "deep_workspace",
        )
        res = export_document(title, paragraphs, output_dir)

        return f"Successfully audited document! Saved in formats: {', '.join(res.get('files', []))}"
    except Exception as e:
        return f"Failed to audit document: {e}"
