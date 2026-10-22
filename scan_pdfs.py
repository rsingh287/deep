import os

from enterprise_rag_finetune import enterprise_rag_ft


def main():
    pdf_dir = "pdf_knowledge_base"

    # Ensure the directory exists
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir, exist_ok=True)
        print(f"Created directory: {pdf_dir}")
        print(
            "Please place your PDF files in this directory and run this script again."
        )
        return

    print("Scanning for PDFs...")
    result = enterprise_rag_ft.ingest_pdfs(pdf_dir=pdf_dir)

    if result.get("success"):
        print(f"Success! Scanned {result.get('files_scanned')} PDFs.")
        if result.get("files_scanned", 0) > 0:
            print(f"Extracted {result.get('pages_extracted')} pages of text.")
            print(
                f"Total documents now in RAG index: {result.get('total_docs_in_index')}"
            )
    else:
        print(f"Failed to scan PDFs: {result.get('error') or result.get('message')}")


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    main()
