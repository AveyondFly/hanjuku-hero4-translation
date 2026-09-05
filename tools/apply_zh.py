#!/usr/bin/env python3
"""Normalize the jp+zh CSVs. Does not touch the ISO.

Source of truth is extracted/translation_catalog.csv (id, jp, zh, notes, kind).
This script only:
  - fills kind
  - copies jp → zh for keep / empty-zh copy rows
  - writes zh_keep.csv and zh_alphabet.csv as filtered views of the same rows

Does not read leftover Python string packs. Edit translation_catalog.csv (jp / zh columns).
zh_keep.csv is a filtered view (always zh = jp). zh_alphabet.csv overlays
the catalog if you edit the name-entry grid there.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zh_csv import (  # noqa: E402
    ALPHABET_CSV,
    CATALOG,
    KEEP_CSV,
    classify,
    load_rows,
    save_rows,
)

def merge_sheet(master: dict[str, dict[str, str]], path: Path) -> int:
    """Overlay zh (and notes) from a special sheet onto matching catalog ids."""
    if not path.exists():
        return 0
    n = 0
    for row in load_rows(path):
        sid = row["id"]
        if sid not in master:
            continue
        dst = master[sid]
        if row.get("zh") != dst.get("zh") or row.get("notes") != dst.get("notes"):
            dst["zh"] = row.get("zh") or ""
            if row.get("notes"):
                dst["notes"] = row["notes"]
            n += 1
    return n


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()

    rows = load_rows()
    by_id = {r["id"]: r for r in rows}
    n_sheet = merge_sheet(by_id, ALPHABET_CSV)

    n_kind = n_keep = n_copy = 0
    for row in rows:
        kind = classify(row["id"], row.get("jp") or "")
        if row.get("kind") != kind:
            n_kind += 1
        row["kind"] = kind
        jp = row.get("jp") or ""
        zh = row.get("zh") or ""
        if kind == "keep":
            if zh != jp:
                n_keep += 1
            row["zh"] = jp
        elif kind == "copy" and not zh.strip() and jp.strip():
            row["zh"] = jp
            n_copy += 1

    save_rows(rows)
    save_rows([r for r in rows if r["kind"] == "keep"], KEEP_CSV)
    save_rows([r for r in rows if r["kind"] == "alphabet"], ALPHABET_CSV)

    kinds = Counter(r["kind"] for r in rows)
    filled = sum(1 for r in rows if (r.get("zh") or "").strip())
    print(
        f"catalog {len(rows)}  zh {filled}  "
        f"kind_fix {n_kind}  keep_fill {n_keep}  copy_fill {n_copy}  "
        f"sheet_merge {n_sheet}"
    )
    print("kinds", dict(kinds))
    print("wrote", CATALOG)
    print("wrote", KEEP_CSV)
    print("wrote", ALPHABET_CSV)


if __name__ == "__main__":
    main()
