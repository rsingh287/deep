import json
import os
import re

import requests

from advanced_document_exporter import export_document


def run_grammar_auditor(document_text: str) -> str:
    """Uses Ollama to audit and improve the grammar, tone, and readability of a document."""
    ollama_base = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    if not ollama_base.startswith("http://") and not ollama_base.startswith("https://"):
        ollama_base = f"http://{ollama_base}"
    url = f"{ollama_base}/api/generate"

    system = (
        "You are an expert Document Editor and Grammar Auditor. "
        "The user will provide the text of a document. "
        "You must improve the grammar, rewrite passive voice to active voice, "
        "and improve the readability and impact (especially for resumes). "
        "You must output ONLY valid JSON with no extra markdown text. "
        "The JSON format should be: "
        '{"title": "Audited_Document", "paragraphs": ["paragraph 1", "paragraph 2", ...] }'
    )

    model_tag = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

    payload = {
        "model": model_tag,
        "prompt": document_text,
        "system": system,
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code != 200:
            return f"Failed to audit document: Ollama server returned HTTP {response.status_code} ({response.text[:150]})"
        data = response.json()
        raw_resp = data.get("response", "{}").strip()
        clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_resp, flags=re.DOTALL).strip()
        try:
            doc_data = json.loads(clean_json)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", clean_json, flags=re.DOTALL)
            if json_match:
                doc_data = json.loads(json_match.group(0))
            else:
                raise
        if not isinstance(doc_data, dict):
            doc_data = {"title": "Audited_Document", "paragraphs": doc_data if isinstance(doc_data, list) else [str(doc_data)]}

        title = doc_data.get("title", "Audited_Document")
        paragraphs = doc_data.get("paragraphs", [])
        if isinstance(paragraphs, str):
            paragraphs = [paragraphs]

        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "generated_apps",
            "deep_workspace",
        )
        res = export_document(title, paragraphs, output_dir)

        files = res.get("files", [])
        if files:
            return f"Successfully audited document! Saved in formats: {', '.join(files)}"
        return "Audited document content, but file export produced 0 output files."
    except Exception as e:
        return f"Failed to audit document: {e}"
