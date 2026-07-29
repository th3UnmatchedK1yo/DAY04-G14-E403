from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import fold_text


TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "source",
}


def _canonical_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    try:
        parts = urlsplit(value)
        host = (parts.hostname or "").lower()
        if not host:
            return value.lower().rstrip("/")
        port = f":{parts.port}" if parts.port else ""
        netloc = host + port
        path = re.sub(r"/+", "/", parts.path).rstrip("/") or "/"
        query = [
            (key, item)
            for key, item in parse_qsl(parts.query, keep_blank_values=True)
            if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
        ]
        return urlunsplit(("", netloc, path, urlencode(sorted(query)), ""))
    except (TypeError, ValueError):
        return value.lower().rstrip("/")


def _canonical_title(value: str) -> str:
    folded = fold_text(value)
    return " ".join(re.findall(r"[a-z0-9]+", folded))


def deduplicate_items(
    items: list[dict[str, Any]] | None = None,
    strategy: str = "url_or_title",
) -> dict[str, Any]:
    """Remove duplicate research items while preserving first-seen order."""
    if strategy not in {"url", "title", "url_or_title"}:
        raise ValueError("strategy must be one of: url, title, url_or_title")

    source_items = items or []
    unique_items: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for item in source_items:
        url_key = _canonical_url(str(item.get("url") or ""))
        title_key = _canonical_title(str(item.get("title") or ""))
        duplicate_by_url = bool(url_key) and url_key in seen_urls
        duplicate_by_title = bool(title_key) and title_key in seen_titles

        is_duplicate = (
            duplicate_by_url
            if strategy == "url"
            else duplicate_by_title
            if strategy == "title"
            else duplicate_by_url or duplicate_by_title
        )
        if is_duplicate:
            continue

        unique_items.append(item)
        if url_key:
            seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)

    return {
        "tool": "deduplicate_results",
        "strategy": strategy,
        "items": unique_items,
        "input_count": len(source_items),
        "item_count": len(unique_items),
        "removed_count": len(source_items) - len(unique_items),
    }
