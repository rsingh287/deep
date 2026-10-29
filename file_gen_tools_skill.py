import json
import os
import re

import requests

from advanced_document_exporter import export_document

OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


def run_file_gen_tools(prompt: str) -> str:
    """Uses Ollama to generate a structured document (resume, cover letter, etc.) and saves it."""
    url = f"{OLLAMA_BASE_URL}/api/generate"

    system = (
        "You are an expert Document and Resume Generator AI. "
        "The user will give you instructions to create a document, such as a resume or a cover letter. "
        "You must output ONLY valid JSON with no extra markdown text. "
        "The JSON format should be: "
        '{"title": "Document Title", "paragraphs": ["paragraph 1", "paragraph 2", ...] }'
    )

    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "system": system,
        "format": "json",
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code != 200:
            return f"Error connecting to Ollama: {response.text}"

        data = response.json()
        result_text = data.get("response", "{}").strip()

        # Strip possible markdown fences
        clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", result_text, flags=re.DOTALL).strip()

        doc_data = json.loads(clean_json)
        title = doc_data.get("title", "Generated_Document")
        paragraphs = doc_data.get("paragraphs", ["Empty document."])

        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "generated_apps",
            "deep_workspace",
        )

        res = export_document(title, paragraphs, output_dir)

        if res.get("status") == "success":
            return f"Successfully generated '{title}'! Saved in formats: {', '.join(res.get('files', []))}"
        else:
            return f"Failed to save document: {res.get('message', 'Unknown export error')}"

    except json.JSONDecodeError:
        return "Failed to generate document: The AI returned invalid JSON."
    except Exception as e:
        return f"Failed to generate document: {e}"
