#!/usr/bin/env python3
# Run inside: distrobox enter <your-box> OR podman run -it python:3.11
# uv run python scripts/verify_dataset.py

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "dataset.csv"
VALID = {"analysis", "hot_take", "reaction"}
MIN_TOTAL = 200
MIN_PCT = 0.20


def main() -> int:
    df = pd.read_csv(CSV)
    exit_code = 0

    dupes = df.duplicated(subset=["text"], keep=False)
    if dupes.any():
        n = dupes.sum()
        print(f"Dropping {n} duplicate rows")
        df = df.drop_duplicates(subset=["text"], keep="first")
        df.to_csv(CSV, index=False)

    print(f"Total: {len(df)}")
    for lbl in sorted(VALID):
        n = (df["label"] == lbl).sum()
        pct = n / len(df) if len(df) else 0
        print(f"  {lbl}: {n} ({pct:.1%})")

    print("\nExamples per label:")
    for lbl in sorted(VALID):
        print(f"\n--- {lbl} ---")
        for _, row in df[df["label"] == lbl].head(3).iterrows():
            print(f"  {row['text'][:120]}...")

    issues = []
    for i, row in df.iterrows():
        if not str(row.get("text", "")).strip():
            issues.append(f"row {i}: empty text")
        if row.get("label") not in VALID:
            issues.append(f"row {i}: invalid label {row.get('label')!r}")
        if len(str(row["text"]).split()) < 10:
            issues.append(f"row {i}: under 10 words")

    if issues:
        print(f"\nFlagged {len(issues)} issues:")
        for msg in issues[:20]:
            print(f"  {msg}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")

    if len(df) < MIN_TOTAL:
        print(f"\nFAIL: total {len(df)} < {MIN_TOTAL}")
        exit_code = 1

    for lbl in VALID:
        pct = (df["label"] == lbl).sum() / len(df) if len(df) else 0
        if pct < MIN_PCT:
            print(f"\nFAIL: {lbl} at {pct:.1%} < {MIN_PCT:.0%}")
            exit_code = 1

    if exit_code == 0:
        print("\nVerification passed.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
