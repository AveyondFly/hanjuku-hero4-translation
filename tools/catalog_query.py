#!/usr/bin/env python3
"""Query or patch extracted/catalog/*.csv without loading a sheet into the editor.

Do not Read/Grep/StrReplace the catalog directory. This CLI prints a small slice.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zh_csv import (  # noqa: E402
    CMAP_CSV,
    catalog_bytes,
    catalog_source,
    load_cmap,
    load_rows,
    save_rows,
    sheet_for_id,
)

DEFAULT_LIMIT = 40
HARD_LIMIT = 200
FIELDS = ("id", "kind", "jp", "zh", "notes")


def _sheet_name(name: str) -> str:
    name = (name or "").strip()
    if name and not name.endswith(".csv"):
        name += ".csv"
    return name


def _trunc(s: str, n: int = 160) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def _row_public(r: dict[str, str]) -> dict[str, str]:
    out = {k: r.get(k) or "" for k in FIELDS}
    out["sheet"] = sheet_for_id(r.get("id") or "")
    return out


def print_rows(rows: list[dict[str, str]], *, as_json: bool, total: int | None = None) -> None:
    if total is None:
        total = len(rows)
    if as_json:
        out = [_row_public(r) for r in rows]
        json.dump({"n": len(rows), "total": total, "rows": out}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    print(f"# {len(rows)} shown / {total} match")
    if total > len(rows):
        print(f"# truncated; narrower filters or --limit {min(total, HARD_LIMIT)}")
    for r in rows:
        sid = r.get("id") or ""
        print(f"{sid}\t{r.get('kind') or ''}\t{sheet_for_id(sid)}")
        print(f"  jp\t{_trunc(r.get('jp') or '')}")
        print(f"  zh\t{_trunc(r.get('zh') or '')}")
        notes = r.get("notes") or ""
        if notes:
            print(f"  notes\t{_trunc(notes)}")


def cmd_get(args: argparse.Namespace) -> int:
    want = list(args.id)
    by_id = {r["id"]: r for r in load_rows()}
    found, missing = [], []
    for sid in want:
        row = by_id.get(sid)
        if row is None:
            missing.append(sid)
        else:
            found.append(row)
    print_rows(found, as_json=args.json)
    if missing:
        print("missing:", ", ".join(missing), file=sys.stderr)
        prefixes = {sid.split("#", 1)[0] for sid in missing}
        hints = [r["id"] for r in by_id.values() if r["id"].split("#", 1)[0] in prefixes]
        if hints[:20]:
            print("nearby ids:", ", ".join(hints[:20]), file=sys.stderr)
        return 1
    return 0


def _filter_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    rows = load_rows()
    id_s = args.id
    jp_s = args.jp
    zh_s = args.zh
    kind = args.kind
    empty_zh = args.empty_zh
    sheet = _sheet_name(getattr(args, "sheet", "") or "")
    out = []
    for r in rows:
        if id_s and id_s not in (r.get("id") or ""):
            continue
        if jp_s and jp_s not in (r.get("jp") or ""):
            continue
        if zh_s and zh_s not in (r.get("zh") or ""):
            continue
        if kind and (r.get("kind") or "") != kind:
            continue
        if empty_zh and (r.get("zh") or "").strip():
            continue
        if sheet and sheet_for_id(r.get("id") or "") != sheet:
            continue
        out.append(r)
    return out


def _apply_limit(rows: list[dict[str, str]], limit: int) -> tuple[list[dict[str, str]], int]:
    limit = min(max(limit, 1), HARD_LIMIT)
    return rows[:limit], len(rows)


def cmd_search(args: argparse.Namespace) -> int:
    if not any((args.id, args.jp, args.zh, args.kind, args.empty_zh, args.sheet)):
        print(
            "search needs --id, --jp, --zh, --kind, --sheet, and/or --empty-zh",
            file=sys.stderr,
        )
        return 2
    shown, total = _apply_limit(_filter_rows(args), args.limit)
    print_rows(shown, as_json=args.json, total=total)
    return 0


def cmd_prefix(args: argparse.Namespace) -> int:
    pfx = args.prefix
    rows = [r for r in load_rows() if r["id"] == pfx or r["id"].startswith(pfx)]
    shown, total = _apply_limit(rows, args.limit)
    print_rows(shown, as_json=args.json, total=total)
    return 0


def cmd_keys(args: argparse.Namespace) -> int:
    from collections import Counter

    c: Counter[str] = Counter()
    for r in load_rows():
        c[r["id"].split("#", 1)[0]] += 1
    items = sorted(c.items())
    if args.match:
        items = [(k, n) for k, n in items if args.match in k]
    total_keys = len(items)
    items = items[: args.limit]
    if args.json:
        json.dump(
            {"n": len(items), "total": total_keys, "keys": [{"id": k, "n": n} for k, n in items]},
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    print(f"# {len(items)} shown / {total_keys} keys")
    for k, n in items:
        print(f"{n:5d}  {k}")
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    if args.zh is None and args.notes is None:
        print("set needs --zh and/or --notes", file=sys.stderr)
        return 2
    rows = load_rows()
    hit = None
    for r in rows:
        if r["id"] == args.id:
            hit = r
            break
    if hit is None:
        print(f"id not found: {args.id}", file=sys.stderr)
        return 1
    if args.zh is not None:
        hit["zh"] = args.zh
    if args.notes is not None:
        hit["notes"] = args.notes
    if args.dry_run:
        print_rows([hit], as_json=args.json)
        print("# dry-run, not written")
        return 0
    save_rows(rows)
    print_rows([hit], as_json=args.json)
    print(f"# wrote {catalog_source()}")
    return 0


def cmd_glyph(args: argparse.Namespace) -> int:
    cmap = load_cmap()
    chars = args.chars
    if args.json:
        rows = []
        for ch in chars:
            g = cmap.get(ch)
            rows.append({"char": ch, "glyph": g, "in_cmap": g is not None})
        json.dump({"file": str(CMAP_CSV), "n_cmap": len(cmap), "rows": rows}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    print(f"# cmap {len(cmap)}  {CMAP_CSV}")
    missing = 0
    for ch in chars:
        g = cmap.get(ch)
        if g is None:
            missing += 1
            print(f"{ch}\tMISSING")
        else:
            print(f"{ch}\t{g}")
    return 1 if missing else 0


def cmd_stats(args: argparse.Namespace) -> int:
    from collections import Counter

    from zh_csv import SHEETS

    rows = load_rows()
    kinds = Counter(r.get("kind") or "" for r in rows)
    sheets = Counter(sheet_for_id(r["id"]) for r in rows)
    filled = sum(1 for r in rows if (r.get("zh") or "").strip())
    src = catalog_source()
    info = {
        "file": str(src),
        "bytes": catalog_bytes(),
        "rows": len(rows),
        "zh_filled": filled,
        "zh_empty": len(rows) - filled,
        "kind": dict(kinds),
        "sheets": {name: sheets.get(name, 0) for name, _ in SHEETS},
    }
    if args.json:
        json.dump(info, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    print(f"file\t{info['file']}")
    print(f"bytes\t{info['bytes']}")
    print(f"rows\t{info['rows']}")
    print(f"zh_filled\t{info['zh_filled']}")
    print(f"zh_empty\t{info['zh_empty']}")
    for k, n in sorted(kinds.items()):
        print(f"kind.{k or '∅'}\t{n}")
    for name, title in SHEETS:
        print(f"sheet.{name}\t{sheets.get(name, 0)}\t{title}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--json", action="store_true", help="JSON instead of text")
        sp.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"max rows (default {DEFAULT_LIMIT}, cap {HARD_LIMIT})")

    g = sub.add_parser("get", help="exact id(s)")
    g.add_argument("id", nargs="+")
    g.add_argument("--json", action="store_true")
    g.set_defaults(func=cmd_get)

    s = sub.add_parser("search", help="substring filters")
    add_common(s)
    s.add_argument("--id", default="", help="id contains")
    s.add_argument("--jp", default="", help="jp contains")
    s.add_argument("--zh", default="", help="zh contains")
    s.add_argument("--kind", default="", help="exact kind")
    s.add_argument("--sheet", default="", help="catalog filename or stem, e.g. ch01_sun")
    s.add_argument("--empty-zh", action="store_true")
    s.set_defaults(func=cmd_search)

    pr = sub.add_parser("prefix", help="id == PREFIX or PREFIX...")
    add_common(pr)
    pr.add_argument("prefix")
    pr.set_defaults(func=cmd_prefix)

    k = sub.add_parser("keys", help="unique id prefixes (before #)")
    add_common(k)
    k.add_argument("--match", default="", help="key contains")
    k.set_defaults(func=cmd_keys)

    st = sub.add_parser("set", help="write zh/notes for one id")
    st.add_argument("id")
    st.add_argument("--zh")
    st.add_argument("--notes")
    st.add_argument("--dry-run", action="store_true")
    st.add_argument("--json", action="store_true")
    st.set_defaults(func=cmd_set)

    gy = sub.add_parser("glyph", help="lookup chars in zh_cmap.csv")
    gy.add_argument("chars", help="characters with no separator, e.g. 抖颤")
    gy.add_argument("--json", action="store_true")
    gy.set_defaults(func=cmd_glyph)

    ss = sub.add_parser("stats", help="row counts")
    ss.add_argument("--json", action="store_true")
    ss.set_defaults(func=cmd_stats)
    return p


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
