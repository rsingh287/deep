"""
Agent-Reach Engine for Antigravity Local AI PC Cockpit
Zero-API-fee internet search aggregator across GitHub, Hacker News, YouTube, and Web.
Inspired by Panniantong/Agent-Reach.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def search_github(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Searches open-source GitHub repositories without API fees."""
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc"
    results = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            for item in data.get("items", [])[:limit]:
                results.append(
                    {
                        "title": item.get("full_name", ""),
                        "stars": item.get("stargazers_count", 0),
                        "description": item.get("description", "")
                        or "No description provided.",
                        "url": item.get("html_url", ""),
                        "language": item.get("language", "Various"),
                    }
                )
    except Exception as e:
        print(f"[AgentReach] GitHub search error: {e}")
    return results


def search_discussions(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Searches real-time tech discussions and community threads via Hacker News Algolia API."""
    url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags=story&hitsPerPage={limit}"
    results = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            for item in data.get("hits", [])[:limit]:
                title = item.get("title", "")
                pts = item.get("points", 0)
                link = (
                    item.get("url")
                    or f"https://news.ycombinator.com/item?id={item.get('objectID')}"
                )
                results.append(
                    {
                        "title": title,
                        "points": pts,
                        "comments": item.get("num_comments", 0),
                        "url": link,
                    }
                )
    except Exception as e:
        print(f"[AgentReach] Discussion search error: {e}")
    return results


def search_youtube_videos(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Searches YouTube and returns video URLs and IDs without API keys."""
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    results = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            unique_ids = list(dict.fromkeys(matches))[:limit]
            for vid in unique_ids:
                results.append(
                    {
                        "title": f"YouTube Video ({vid})",
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "video_id": vid,
                    }
                )
    except Exception as e:
        print(f"[AgentReach] YouTube search error: {e}")
    return results


def multi_reach_search(query: str) -> Dict[str, Any]:
    """
    Executes an Agent-Reach multi-platform query across GitHub, community discussions, and YouTube.
    Returns structured results with clickable links.
    """
    clean_q = query.strip()
    if not clean_q:
        return {"status": "error", "message": "Empty query."}

    gh = search_github(clean_q, limit=3)
    disc = search_discussions(clean_q, limit=3)
    yt = search_youtube_videos(clean_q, limit=2)

    total_hits = len(gh) + len(disc) + len(yt)
    return {
        "status": "success",
        "query": clean_q,
        "total_results": total_hits,
        "github": gh,
        "discussions": disc,
        "youtube": yt,
    }


def format_reach_markdown(data: Dict[str, Any]) -> str:
    """Formats Agent-Reach results into beautiful markdown."""
    q = data.get("query", "")
    md = [f'🌐 **Agent-Reach Live Internet Report: "{q}"**\n']

    # GitHub
    gh = data.get("github", [])
    if gh:
        md.append("### 🐙 Top GitHub Repositories")
        for r in gh:
            md.append(
                f"- [{r['title']}]({r['url']}) ⭐ `{r['stars']:,} stars` ({r['language']})\n  *{r['description']}*"
            )
        md.append("")

    # Discussions
    disc = data.get("discussions", [])
    if disc:
        md.append("### 💬 Community Discussions & Insights")
        for d in disc:
            md.append(
                f"- [{d['title']}]({d['url']}) (`{d['points']} pts`, `{d['comments']} comments`)"
            )
        md.append("")

    # YouTube
    yt = data.get("youtube", [])
    if yt:
        md.append("### 📺 Video Resources")
        for y in yt:
            md.append(f"- [Watch on YouTube]({y['url']})")
        md.append("")

    if not gh and not disc and not yt:
        md.append("No active live discussions found for this query.")

    return "\n".join(md)
