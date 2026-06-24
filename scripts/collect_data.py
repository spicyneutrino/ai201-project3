#!/usr/bin/env python3
# Run inside: distrobox enter <your-box> OR podman run -it python:3.11
# uv run python scripts/collect_data.py

import json
import re
import time
from pathlib import Path

import requests

UA = {"User-Agent": "takemeter-research/1.0"}
MIN_WORDS = 15
MIN_SCORE = 5
TARGET = 350
OUT = Path(__file__).resolve().parent.parent / "raw_posts.json"
PULLPUSH = "https://api.pullpush.io/reddit/search"

# ponytail: Reddit JSON 403 from this host; Pullpush mirrors public r/nba data


def word_count(text: str) -> int:
    return len(text.split())


def url_only(text: str) -> bool:
    return bool(re.fullmatch(r"https?://\S+", text.strip()))


def passes_filter(text: str, author: str, score: int) -> bool:
    if not text or not text.strip():
        return False
    if author == "AutoModerator":
        return False
    if score < MIN_SCORE:
        return False
    if text.strip().lower().startswith("i am a bot"):
        return False
    if word_count(text) < MIN_WORDS:
        return False
    if url_only(text):
        return False
    return True


def fetch_pullpush(kind: str, params: dict) -> list[dict]:
    r = requests.get(f"{PULLPUSH}/{kind}/", params=params, headers=UA, timeout=90)
    r.raise_for_status()
    return r.json().get("data", [])


def main() -> None:
    seen: set[str] = set()
    results: list[dict] = []

    def add(text: str, score: int, author: str) -> None:
        text = text.strip()
        if text in seen or not passes_filter(text, author, score):
            return
        seen.add(text)
        results.append({"text": text, "score": score})

    queries = [
        ("submission", {"subreddit": "nba", "sort": "desc", "sort_type": "score", "size": 100}),
        ("submission", {"subreddit": "nba", "sort": "desc", "sort_type": "created_utc", "size": 100}),
        ("submission", {"subreddit": "nba", "sort": "desc", "sort_type": "num_comments", "size": 100}),
        ("comment", {"subreddit": "nba", "sort": "desc", "sort_type": "score", "size": 100}),
        ("comment", {"subreddit": "nba", "sort": "desc", "sort_type": "created_utc", "size": 100}),
    ]

    print("Collecting via Pullpush (Reddit JSON blocked from this host)")
    for kind, base in queries:
        before = None
        for page in range(6):
            if len(results) >= TARGET:
                break
            params = dict(base)
            if before:
                params["before"] = before
            print(f"  {kind} page {page + 1}...", flush=True)
            batch = fetch_pullpush(kind, params)
            if not batch:
                break
            for item in batch:
                if kind == "submission":
                    title = item.get("title", "")
                    selftext = item.get("selftext", "")
                    text = f"{title} {selftext}".strip() if selftext else title
                else:
                    text = item.get("body", "")
                add(text, item.get("score", 0), item.get("author", ""))
            before = batch[-1].get("created_utc")
            time.sleep(0.5)
        if len(results) >= TARGET:
            break

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Collected {len(results)} raw examples -> {OUT}")


if __name__ == "__main__":
    main()
