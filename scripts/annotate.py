#!/usr/bin/env python3
# Run inside: distrobox enter <your-box> OR podman run -it python:3.11
# uv run python scripts/annotate.py

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw_posts.json"
OUT = ROOT / "dataset.csv"
ERRORS = ROOT / "annotation_errors.txt"
PER_LABEL = 70
TARGET = 210
VALID = {"analysis", "hot_take", "reaction"}
MODEL = "llama-3.3-70b-versatile"

PROMPT = '''You are labeling NBA Reddit posts for a discourse quality classifier.

Labels:
- analysis: structured argument backed by specific stats or historical data
- hot_take: bold confident opinion with no real evidence, asserts rather than argues
- reaction: immediate emotional response to a specific event, short and feeling-based

Post to label:
"{text}"

Respond with exactly one word: analysis, hot_take, or reaction. No other output.'''


def label_post(client: Groq, text: str) -> str | None:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT.format(text=text.replace('"', "'"))}],
        temperature=0,
        max_tokens=10,
    )
    raw = (resp.choices[0].message.content or "").strip().lower()
    label = raw.split()[0].rstrip(".,;:!?") if raw else ""
    return label if label in VALID else None


def main() -> None:
    load_dotenv(ROOT / ".env")
    client = Groq()
    posts = json.loads(RAW.read_text(encoding="utf-8"))
    buckets: dict[str, list[dict]] = defaultdict(list)
    used_texts: set[str] = set()
    if OUT.exists():
        existing = pd.read_csv(OUT)
        for _, row in existing.iterrows():
            buckets[row["label"]].append(
                {"text": row["text"], "label": row["label"], "notes": row.get("notes", "")}
            )
            used_texts.add(row["text"])
        print(f"Resuming: {sum(len(buckets[l]) for l in VALID)} rows already labeled")
    errors: list[str] = []
    labeled = 0

    for i, item in enumerate(posts):
        if item["text"] in used_texts:
            continue
        if all(len(buckets[l]) >= PER_LABEL for l in VALID):
            break
        text = item["text"]
        try:
            label = label_post(client, text)
        except Exception as e:
            errors.append(f"API error on item {i}: {e}")
            time.sleep(2)
            continue
        labeled += 1
        if label is None:
            errors.append(f"Invalid label item {i}: {text[:80]!r}")
            continue
        if len(buckets[label]) < PER_LABEL:
            buckets[label].append({"text": text, "label": label, "notes": ""})
        if labeled % 20 == 0:
            counts = {l: len(buckets[l]) for l in VALID}
            print(f"Labeled {labeled}, counts: {counts}", flush=True)
        time.sleep(0.25)

    rows = []
    for lbl in sorted(VALID):
        rows.extend(buckets[lbl])

    if errors:
        ERRORS.write_text("\n".join(errors) + "\n", encoding="utf-8")

    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)

    print("\nLabel distribution:")
    for lbl in sorted(VALID):
        n = len(buckets[lbl])
        pct = 100 * n / len(df) if len(df) else 0
        print(f"  {lbl}: {n} ({pct:.1f}%)")
        if len(df) and pct < 20:
            print(f"  WARNING: {lbl} below 20%")
    print(f"\nWrote {len(df)} rows -> {OUT}")


if __name__ == "__main__":
    main()
