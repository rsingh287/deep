"""
Advanced Web Scraper Engine
Provides robust web scraping, table extraction, and text summarization from generic URLs.
"""

import json

import requests
from bs4 import BeautifulSoup


def fetch_webpage_text(url: str) -> str:
    """Fetches and cleans visible text from any URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=" ")
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text[:10000]  # Return top 10k chars to avoid blowing up context
    except Exception as e:
        return f"Error fetching {url}: {e}"


def extract_tables_as_json(url: str) -> str:
    """Extracts all HTML tables from a URL and returns them as a JSON string."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        tables = soup.find_all("table")
        result = []
        for i, table in enumerate(tables):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                if cells:
                    rows.append(cells)
            if rows:
                result.append({"table_index": i, "data": rows})

        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error extracting tables from {url}: {e}"


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    # Test script
    print(
        fetch_webpage_text("https://en.wikipedia.org/wiki/Artificial_intelligence")[
            :500
        ]
    )
