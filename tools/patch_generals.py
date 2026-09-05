#!/usr/bin/env python3
"""Patch general card names (and known hobbies) in the 100-byte unit table.

The table is inside VFS slot 0 (LBA 300), starting at ISO offset of gen_no2.
Each record is 100 bytes:
  0x00 ASCII id
  0x22 font-coded display name (C10 extra 91 … C2)
  0x43 font-coded hobby (no wrapper; NUL padded)

The engine shows record[i].name on the following unit; we only replace bytes
in place so indexing does not matter.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mes_codec import decode_font_codes, encode_tokens, glyph_to_char  # noqa: E402
from patch_iso import ISO, SECTOR  # noqa: E402
from zh_csv import (  # noqa: E402
    CATALOG_DIR,
    classify,
    load_cmap,
    load_rows,
    save_rows,
)

TABLE_ID = b"gen_no2\x00"
REC = 100
NAME_OFF, NAME_END = 0x22, 0x40
HOBBY_OFF, HOBBY_END = 0x43, 0x64
PREFIX = ("C", 10, 91)
SUFFIX = ("C", 2, None)


def glyph_char(code) -> str:
    if code == 175:
        return "ヴ"
    return glyph_to_char(code)


def decode_field(raw: bytes) -> str:
    raw = raw.split(b"\x00", 1)[0]
    if not raw:
        return ""
    codes = decode_font_codes(raw + b"\x00", mul48=False)
    chars = []
    for c in codes:
        if isinstance(c, tuple):
            continue
        chars.append(glyph_char(c))
    s = "".join(chars)
    out = []
    for i, ch in enumerate(s):
        if ch == "っ" and i > 0 and "\u30a0" <= s[i - 1] <= "\u30ff":
            out.append("ッ")
        else:
            out.append(ch)
    return "".join(out)


def encode_name(zh: str, cmap: dict[str, int]) -> bytes:
    body = []
    for ch in zh:
        g = cmap.get(ch)
        if g is None:
            raise ValueError(f"not in cmap: {ch!r}")
        body.append(g)
    raw = encode_tokens([PREFIX, *body, SUFFIX], mul48=True)
    room = NAME_END - NAME_OFF
    if len(raw) > room:
        raise ValueError(f"name too long {zh!r} {len(raw)}>{room}")
    return raw.ljust(room, b"\x00")


def encode_hobby(zh: str, cmap: dict[str, int]) -> bytes:
    toks = []
    for ch in zh:
        g = cmap.get(ch)
        if g is None:
            raise ValueError(f"not in cmap: {ch!r}")
        toks.append(g)
    raw = encode_tokens(toks, mul48=True)
    room = HOBBY_END - HOBBY_OFF
    if len(raw) > room:
        raise ValueError(f"hobby too long {zh!r} {len(raw)}>{room}")
    return raw.ljust(room, b"\x00")


def looks_garbage(name: str) -> bool:
    if "{" in name or len(name) > 18:
        return True
    return name.count("よ") >= 6


def _split_generals(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    names: dict[str, dict[str, str]] = {}
    hobbies: dict[str, dict[str, str]] = {}
    for row in rows:
        sid = row.get("id") or ""
        if not sid.startswith("gen_"):
            continue
        if "#hobby" in sid:
            hobbies[sid.split("#", 1)[0]] = row
        else:
            names[sid] = row
    return names, hobbies


def main() -> None:
    cmap = load_cmap()
    catalog = load_rows()
    names, hobbies = _split_generals(catalog)
    print(f"re-encode from catalog ({len(names)} names, {len(hobbies)} hobbies)")

    with ISO.open("rb") as fp:
        fp.seek(300 * SECTOR)
        window = fp.read(400_000)
    rel = window.find(TABLE_ID)
    if rel < 0:
        raise SystemExit("gen_no2 table not found near LBA 300")
    start = 300 * SECTOR + rel
    print(f"table at {start} LBA {start // SECTOR}")

    gen_rows: list[dict[str, str]] = []
    patched_name = patched_hobby = skipped = 0
    off = 0
    n = 0
    with ISO.open("r+b") as fp:
        fp.seek(start)
        blob = bytearray(fp.read(700 * REC))

        while off + REC <= len(blob) and n < 700:
            rec = bytearray(blob[off : off + REC])
            if not rec.startswith(b"gen_"):
                break
            z = rec.find(b"\x00")
            gid = bytes(rec[:z]).decode("ascii")
            prev_n = names.get(gid)
            prev_h = hobbies.get(gid)
            if prev_n and (prev_n.get("jp") or "").strip():
                jp_n = prev_n["jp"]
            else:
                jp_n = decode_field(bytes(rec[NAME_OFF:NAME_END]))
            if prev_h and (prev_h.get("jp") or "").strip():
                jp_h = prev_h["jp"]
            else:
                jp_h = decode_field(bytes(rec[HOBBY_OFF:HOBBY_END]))
            notes = (prev_n or {}).get("notes") or ""
            if looks_garbage(jp_n):
                skipped += 1
                gen_rows.append(
                    {
                        "id": gid,
                        "jp": jp_n,
                        "zh": "",
                        "notes": notes or "skipped garbage",
                        "kind": classify(gid, jp_n),
                    }
                )
                if jp_h:
                    hid = f"{gid}#hobby"
                    gen_rows.append(
                        {
                            "id": hid,
                            "jp": jp_h,
                            "zh": "",
                            "notes": "",
                            "kind": classify(hid, jp_h),
                        }
                    )
                off += REC
                n += 1
                continue
            zh_n = ((prev_n or {}).get("zh") or "").strip()
            zh_h = ((prev_h or {}).get("zh") or "").strip()
            if zh_n and zh_n != jp_n:
                try:
                    rec[NAME_OFF:NAME_END] = encode_name(zh_n, cmap)
                    patched_name += 1
                except ValueError as e:
                    notes = str(e)
                    skipped += 1
            if zh_h and zh_h != jp_h:
                try:
                    rec[HOBBY_OFF:HOBBY_END] = encode_hobby(zh_h, cmap)
                    patched_hobby += 1
                except ValueError as e:
                    notes = (notes + "; " if notes else "") + str(e)
            blob[off : off + REC] = rec
            gen_rows.append(
                {
                    "id": gid,
                    "jp": jp_n,
                    "zh": zh_n,
                    "notes": notes,
                    "kind": classify(gid, jp_n),
                }
            )
            if jp_h or zh_h:
                hid = f"{gid}#hobby"
                gen_rows.append(
                    {
                        "id": hid,
                        "jp": jp_h,
                        "zh": zh_h,
                        "notes": "",
                        "kind": classify(hid, jp_h),
                    }
                )
            off += REC
            n += 1

        fp.seek(start)
        fp.write(bytes(blob[:off]))

    merged = [r for r in catalog if not (r.get("id") or "").startswith("gen_")]
    merged.extend(gen_rows)
    save_rows(merged)
    print(f"patched names {patched_name} hobbies {patched_hobby} skipped {skipped}")
    print(f"wrote {CATALOG_DIR / 'generals.csv'} ({len(gen_rows)} rows)")
    print(f"wrote table {off} bytes at {start}")


if __name__ == "__main__":
    main()
