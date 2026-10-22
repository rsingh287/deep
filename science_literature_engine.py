"""
Science Literature Engine
Provides capability to search arXiv for research papers, download PDFs,
and extract metadata (abstract, authors, publish date).
"""

import json
import os

import arxiv


def search_and_download_papers(
    query: str, max_results: int = 3, download_dir: str = "."
) -> str:
    """
    Searches arXiv for papers matching the query, returns metadata as JSON,
    and downloads the PDFs locally.
    """
    try:
        # Create dir if not exists
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Construct the default API client
        client = arxiv.Client()

        # Search
        search = arxiv.Search(
            query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
        )

        results = []
        for result in client.results(search):
            paper_info = {
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "published": result.published.strftime("%Y-%m-%d"),
                "summary": result.summary.replace("\n", " ")[:500] + "...",
                "pdf_url": result.pdf_url,
            }
            results.append(paper_info)

            # Download PDF
            filename = f"{result.get_short_id()}.pdf"
            result.download_pdf(dirpath=download_dir, filename=filename)
            paper_info["downloaded_path"] = os.path.join(download_dir, filename)

        return json.dumps(
            {"query": query, "results_count": len(results), "papers": results}, indent=2
        )

    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # Test script
    print(
        search_and_download_papers(
            "quantum computing error correction", max_results=1, download_dir="papers"
        )
    )
