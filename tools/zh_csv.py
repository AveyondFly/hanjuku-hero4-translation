"""Load / save the jp+zh CSVs.

Mes strings live in extracted/translation_catalog.csv (id, jp, zh, notes, kind).
The font mapping is a different schema, so it stays in extracted/zh_cmap.csv.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACTED = ROOT / "extracted"
CATALOG = EXTRACTED / "translation_catalog.csv"
CMAP_CSV = EXTRACTED / "zh_cmap.csv"
KEEP_CSV = EXTRACTED / "zh_keep.csv"
ALPHABET_CSV = EXTRACTED / "zh_alphabet.csv"

FIELDNAMES = ["id", "jp", "zh", "notes", "kind"]

# Must stay original glyph ids (kana input / 合言葉). patch_iso transcodes only.
KEEP_PREFIXES = (
    "sysmes_hiragana",
    "sysmes_katakana",
    "sysmes_dic_index_keyword",
    "menu_secret_egg_word",
)

# Name-entry grid: jp is kanji sharing those slots, zh is A–Z / digits.
ALPHABET_PREFIXES = ("sysmes_alphabet",)

# 1–2 glyph UI marks copied from jp; re-encoded through the Chinese cmap.
COPY_PREFIXES = (
    "sysmes_hyphen",
    "sysmes_question",
    "sysmes_battle_status",
    "sysmes_battle_status_enemy",
    "sysmes_egg_type_mark",
    "sysmes_egg_type_mark_broken",
    "sysmes_field_base_mark",
    "sysmes_formation_mark",
    "sysmes_term_b",
    "sysmes_term_k",
)


def id_matches(sid: str, prefixes: tuple[str, ...]) -> bool:
    for pfx in prefixes:
        if sid == pfx or sid.startswith(pfx + "#"):
            return True
    return False


def classify(sid: str, jp: str) -> str:
    if id_matches(sid, ALPHABET_PREFIXES):
        return "alphabet"
    if id_matches(sid, KEEP_PREFIXES):
        return "keep"
    if not (jp or "").strip():
        return "empty"
    if id_matches(sid, COPY_PREFIXES):
        return "copy"
    return "text"


def load_rows(path: Path = CATALOG) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "id": row.get("id") or "",
                    "jp": row.get("jp") or "",
                    "zh": row.get("zh") or "",
                    "notes": row.get("notes") or "",
                    "kind": row.get("kind") or "",
                }
            )
    return rows


def save_rows(rows: list[dict[str, str]], path: Path = CATALOG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) or "" for k in FIELDNAMES})


def zh_by_id(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    if rows is None:
        rows = load_rows()
    return {r["id"]: r.get("zh") or "" for r in rows}


def kinds_by_id(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    if rows is None:
        rows = load_rows()
    return {r["id"]: r.get("kind") or classify(r["id"], r.get("jp") or "") for r in rows}


def load_cmap(path: Path = CMAP_CSV) -> dict[str, int]:
    out: dict[str, int] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ch = row.get("char") or ""
            if ch:
                out[ch] = int(row["glyph"])
    return out


def keep_raw(sid: str, kind: str = "") -> bool:
    if kind == "keep":
        return True
    return id_matches(sid, KEEP_PREFIXES)
