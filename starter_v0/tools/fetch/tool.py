from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import requests

from env_loader import load_lab_env
from tools._shared import TIMEOUT, domain, err
from tools.lookup.tool import web_search

ROOT = Path(__file__).resolve().parent.parent.parent
load_lab_env(ROOT)


def _fallback_fetch(url: str) -> dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    html = resp.text

    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else url

    clean_text = re.sub(r"<(script|style).*?>.*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL)
    clean_text = re.sub(r"<.*?>", " ", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return {
        "tool": "read_url",
        "url": url,
        "items": [{
            "title": title,
            "url": url,
            "source": domain(url),
            "summary": clean_text[:4000],
        }],
    }


def read_url(url: str = "") -> dict[str, Any]:
    if not url or not str(url).strip():
        return err("read_url", "Missing URL or query parameter")

    target = str(url).strip()

    # Smart Search & Fetch Integration:
    # If the user provides a query string instead of a valid HTTP/HTTPS URL,
    # automatically perform a Web Search first to locate the top relevant URL.
    if not (target.startswith("http://") or target.startswith("https://")):
        search_res = web_search(query=target, max_results=3)
        if search_res.get("items") and isinstance(search_res["items"], list) and len(search_res["items"]) > 0:
            first_url = search_res["items"][0].get("url")
            if first_url:
                target = first_url

    if not (target.startswith("http://") or target.startswith("https://")):
        return err("read_url", f"Invalid URL or no search results found for: {url}")

    # 1. Try Firecrawl API for scraping markdown
    try:
        key = os.getenv("FIRECRAWL_API_KEY")
        if key:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                json={"url": target, "formats": ["markdown"]},
                headers={"Authorization": f"Bearer {key}"},
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                meta = data.get("metadata", {}) or {}
                markdown_content = data.get("markdown") or ""
                if markdown_content:
                    return {
                        "tool": "read_url",
                        "url": target,
                        "items": [{
                            "title": meta.get("title") or target,
                            "url": meta.get("sourceURL") or target,
                            "source": domain(target),
                            "summary": markdown_content[:4000],
                        }],
                    }
    except Exception:
        pass

    # 2. Fallback to direct HTTP fetch
    try:
        return _fallback_fetch(target)
    except Exception as exc:
        return err("read_url", exc)
