"""
===================================================================
CRAWL4AI CLEAN MARKDOWN EXTRACTION ENGINE
===================================================================
Transforms dynamic, JavaScript-rendered web pages into clean,
structured Markdown tailored for LLM reasoning and RAG knowledge bases.
Uses crawl4ai AsyncWebCrawler with resilient fallback.
"""

import asyncio
import sys
from typing import Any, Dict, Optional

# Ensure Windows terminal outputs UTF-8 cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


async def _crawl_async(
    url: str, css_selector: Optional[str] = None, bypass_cache: bool = True
) -> Dict[str, Any]:
    """Internal coroutine for crawling via Crawl4ai with fallback."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Try native Crawl4ai AsyncWebCrawler
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

        browser_cfg = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        run_cfg = CrawlerRunConfig(
            css_selector=css_selector,
            cache_mode=CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED,
            word_count_threshold=10,
            remove_overlay_elements=True,
        )

        async with AsyncWebCrawler(config=browser_cfg) as crawler:
            result = await crawler.arun(url=url, config=run_cfg)
            if result.success:
                raw_markdown = result.markdown
                if hasattr(raw_markdown, "raw_markdown"):
                    clean_md = raw_markdown.raw_markdown
                elif (
                    hasattr(raw_markdown, "fit_markdown") and raw_markdown.fit_markdown
                ):
                    clean_md = raw_markdown.fit_markdown
                else:
                    clean_md = str(raw_markdown)

                page_title = (
                    getattr(result, "metadata", {}).get("title", "")
                    if getattr(result, "metadata", None)
                    else ""
                )

                return {
                    "status": "success",
                    "engine": "crawl4ai",
                    "url": url,
                    "title": page_title or "Extracted Web Page",
                    "markdown": clean_md,
                    "char_count": len(clean_md),
                    "media_count": len(getattr(result, "media", []) or []),
                    "links_count": len(
                        getattr(result, "links", {}).get("internal", []) or []
                    ),
                }
    except Exception as e:
        print(
            f"[Crawl4ai] Notice: Crawl4ai encountered: {str(e)[:120]}. Falling back to Playwright..."
        )

    # Resilient Playwright + Markdown Fallback
    try:
        from bs4 import BeautifulSoup
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(1.5)

            title = await page.title()
            html = await page.content()
            await browser.close()

            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(
                ["script", "style", "svg", "noscript", "iframe", "nav", "footer"]
            ):
                tag.decompose()

            if css_selector:
                selected = soup.select(css_selector)
                if selected:
                    soup = BeautifulSoup(
                        "".join(str(s) for s in selected), "html.parser"
                    )

            md_lines = []
            if title:
                md_lines.append(f"# {title}\n")

            for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
                if elem.name == "h1":
                    md_lines.append(f"\n# {elem.get_text(strip=True)}\n")
                elif elem.name == "h2":
                    md_lines.append(f"\n## {elem.get_text(strip=True)}\n")
                elif elem.name == "h3":
                    md_lines.append(f"\n### {elem.get_text(strip=True)}\n")
                elif elem.name == "li":
                    md_lines.append(f"- {elem.get_text(strip=True)}")
                elif elem.name == "p":
                    text = elem.get_text(strip=True)
                    if text:
                        md_lines.append(f"\n{text}\n")
                elif elem.name == "table":
                    rows = elem.find_all("tr")
                    for r in rows:
                        cols = [
                            td.get_text(strip=True) for td in r.find_all(["td", "th"])
                        ]
                        if cols:
                            md_lines.append("| " + " | ".join(cols) + " |")

            clean_md = "\n".join(md_lines).strip()
            return {
                "status": "success",
                "engine": "playwright_markdown_fallback",
                "url": url,
                "title": title or "Extracted Page",
                "markdown": clean_md,
                "char_count": len(clean_md),
            }
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "message": f"All crawl attempts failed: {str(e)}",
        }


def crawl_clean_markdown(
    url: str, css_selector: Optional[str] = None, bypass_cache: bool = True
) -> Dict[str, Any]:
    """Synchronous interface for Crawl4ai clean markdown extraction."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(
                _crawl_async(url, css_selector, bypass_cache)
            )
        else:
            return asyncio.run(_crawl_async(url, css_selector, bypass_cache))
    except RuntimeError:
        return asyncio.run(_crawl_async(url, css_selector, bypass_cache))


if __name__ == "__main__":
    test_target = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/html"
    res = crawl_clean_markdown(test_target)
    print("Status:", res.get("status"))
    print("Engine:", res.get("engine"))
    print("Title:", res.get("title"))
    print("Markdown Preview:\n", res.get("markdown", "")[:250])
