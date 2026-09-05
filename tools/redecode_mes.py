#!/usr/bin/env python3
"""Re-decode extracted/mes/*.bin with the current mes_codec map.

Does not touch the ISO. Use after editing SPECIAL in mes_codec.py.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mes_codec import SPECIAL, decode_string, walk_trie  # noqa: E402
from zh_csv import CATALOG, classify, load_rows, save_rows  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MES = ROOT / "extracted" / "mes"
TEXT = ROOT / "extracted" / "text"


def main() -> None:
    TEXT.mkdir(parents=True, exist_ok=True)
    bins = sorted(MES.glob("ram_*.bin")) + sorted(
        p for p in MES.glob("*.bin") if not p.name.startswith("ram_")
    )
    catalog: list[tuple[str, str, str]] = []
    all_lines: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for bp in bins:
        data = bp.read_bytes()
        tag = bp.stem
        rows = walk_trie(data)
        lines = []
        for key, strs in sorted(rows, key=lambda x: x[0]):
            k = key.decode("latin1", "replace")
            lines.append(f"### {k}  lines={len(strs)}")
            for i, raw in enumerate(strs):
                jp = decode_string(raw)
                lines.append(f"  [{i}] {jp}")
                sid = k if len(strs) == 1 else f"{k}#{i}"
                all_lines.append((sid, jp, tag))
                if sid not in seen:
                    seen.add(sid)
                    catalog.append((sid, jp, tag))
            lines.append("")
        (TEXT / f"{tag}.txt").write_text("\n".join(lines), encoding="utf-8")

    old_zh: dict[str, str] = {}
    old_kind: dict[str, str] = {}
    if CATALOG.exists():
        for row in load_rows():
            if (row.get("zh") or "").strip():
                old_zh[row["id"]] = row["zh"]
            if row.get("kind"):
                old_kind[row["id"]] = row["kind"]

    out_rows = [
        {
            "id": sid,
            "jp": jp,
            "zh": old_zh.get(sid, ""),
            "notes": tag,
            "kind": old_kind.get(sid) or classify(sid, jp),
        }
        for sid, jp, tag in catalog
    ]
    save_rows(out_rows)
    print(f"preserved zh {len(old_zh)} -> {CATALOG}")

    with (TEXT / "ALL_DECODED.txt").open("w", encoding="utf-8") as f:
        cur = None
        for sid, jp, tag in all_lines:
            if tag != cur:
                f.write(f"\n\n======== {tag} ========\n")
                cur = tag
            f.write(f"{sid}\t{jp}\n")

    text = "\n".join(jp for _, jp, _ in catalog)
    codes = Counter(int(x) for x in re.findall(r"\{(\d+)\}", text))
    n_brace = sum(1 for _, jp, _ in catalog if "{" in jp)
    print(f"SPECIAL {len(SPECIAL)}  catalog {len(catalog)}")
    print(f"unmapped unique {len(codes)} occ {sum(codes.values())}")
    print(f"catalog rows with {{n}} {n_brace}/{len(catalog)}")
    print("top15", codes.most_common(15))

    font_dir = ROOT / "font"
    font_dir.mkdir(parents=True, exist_ok=True)
    ctx_lines: list[str] = []
    for code, n in codes.most_common():
        token = f"{{{code}}}"
        ctx_lines.append(f"==== {code}  n={n} ====")
        shown = 0
        for sid, jp, _tag in catalog:
            if token not in jp:
                continue
            s = jp.replace("\n", " ")
            i = s.find(token)
            win = s[max(0, i - 24) : i + 40]
            win = win.replace(token, f"【{code}】")
            ctx_lines.append(f"  {win}")
            shown += 1
            if shown >= 5:
                break
        ctx_lines.append("")
    (font_dir / "unmapped_context.txt").write_text(
        "\n".join(ctx_lines) if ctx_lines else "(none)\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
