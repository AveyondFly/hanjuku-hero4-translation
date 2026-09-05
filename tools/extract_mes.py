#!/usr/bin/env python3
"""Extract and decode all message files from the ISO + resume RAM."""
from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mes_codec import (  # noqa: E402
    codes_to_text,
    decode_font_codes,
    decode_string,
    looks_like_mes,
    walk_trie,
)
from zh_csv import CATALOG_DIR, classify, load_rows, preserve_extra_rows, save_rows  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ISO = ROOT / "半熟英雄4-7人的半熟英雄.iso"
ELF = ROOT / "extracted/SLPM_658.39"
RAM = ROOT / "extracted/ram/eeMemory.bin"
OUT = ROOT / "extracted"
MES_OUT = OUT / "mes"
TEXT_OUT = OUT / "text"

LOAD_V = 0x210000
LOAD_FILE = 0x1000
TABLE_VA = 0x432C48
TABLE_N = 19967
SECTOR = 2048
LBA_MIN, LBA_MAX = 300, 931017


def fo(va: int) -> int:
    return va - LOAD_V + LOAD_FILE


def parse_hash_table(buf: bytes, off: int) -> list[tuple[int, int, int, int]]:
    out = []
    for i in range(TABLE_N):
        a, b, c = struct.unpack_from("<III", buf, off + i * 12)
        if a or b or c:
            out.append((i, a, b, c))
    return out


def dump_mes_file(data: bytes, dest_txt: Path, dest_bin: Path | None = None) -> int:
    if dest_bin is not None:
        dest_bin.write_bytes(data)
    rows = walk_trie(data)
    lines = []
    nstr = 0
    for key, strs in sorted(rows, key=lambda x: x[0]):
        k = key.decode("latin1", "replace")
        lines.append(f"### {k}  lines={len(strs)}")
        for i, raw in enumerate(strs):
            text = decode_string(raw)
            lines.append(f"  [{i}] {text}")
            nstr += 1
        lines.append("")
    dest_txt.write_text("\n".join(lines), encoding="utf-8")
    return nstr


def main() -> None:
    MES_OUT.mkdir(parents=True, exist_ok=True)
    TEXT_OUT.mkdir(parents=True, exist_ok=True)

    # --- sanity cribs from RAM sysmes ---
    ram = RAM.read_bytes()
    sysmes = ram[0x0071E580 : 0x0071E580 + 0x38F0]
    bykey = {k.decode("latin1"): strs for k, strs in walk_trie(sysmes)}
    print("CRIB title_term:")
    for s in bykey["sysmes_title_term"]:
        print(" ", decode_string(s), " codes", decode_font_codes(s))
    print("CRIB parameter:")
    for s in bykey["sysmes_parameter"]:
        print(" ", decode_string(s), decode_font_codes(s))
    print("CRIB pause", decode_string(bykey["sysmes_pause"][0]))
    print("CRIB planet:")
    for s in bykey["sysmes_planet_name"]:
        print(" ", decode_string(s))

    # --- dump 5 RAM mes ---
    ram_files = [
        (0x006FC380, 0x2150, "ram_974_weekday"),
        (0x006FEC40, 0x10A8, "ram_1004_fmenu"),
        (0x007004C0, 0x1DC10, "ram_1006_menu"),
        (0x0071E580, 0x38F0, "ram_1005_sysmes"),
        (0x00722600, 0x2870, "ram_1007_debug"),
    ]
    catalog: list[tuple[str, str, str]] = []  # id, jp, notes
    for addr, size, name in ram_files:
        data = ram[addr : addr + size]
        n = dump_mes_file(data, TEXT_OUT / f"{name}.txt", MES_OUT / f"{name}.bin")
        print(f"RAM {name}: {n} lines")
        for key, strs in walk_trie(data):
            k = key.decode("latin1", "replace")
            for i, raw in enumerate(strs):
                jp = decode_string(raw)
                sid = k if len(strs) == 1 else f"{k}#{i}"
                catalog.append((sid, jp, name))

    # --- ISO files via hash table ---
    elf = ELF.read_bytes()
    entries = parse_hash_table(elf, fo(TABLE_VA))
    # unique LBA+size where field0 looks like LBA and field2 like size
    files = {}
    for slot, lba, size, flags in entries:
        if not (LBA_MIN <= lba <= LBA_MAX):
            continue
        if not (32 <= size <= 8 * 1024 * 1024):
            continue
        files.setdefault((lba, size), (slot, flags))
    print(f"hash unique files {len(files)} (from {len(entries)} filled slots)")

    iso_size = ISO.stat().st_size
    mes_index = []
    n_mes = 0
    magics = Counter()
    n_probe = 0
    with ISO.open("rb") as fp:
        for (lba, size), (slot, flags) in sorted(files.items()):
            off = lba * SECTOR
            if off + 4 > iso_size:
                continue
            fp.seek(off)
            head = fp.read(16)
            if len(head) < 4:
                continue
            magics[head[:4]] += 1
            root = struct.unpack_from("<I", head, 0)[0]
            if root < 4 or root + 8 > size or off + root + 8 > iso_size:
                continue
            fp.seek(off + root)
            node = fp.read(8)
            if len(node) < 8:
                continue
            nkey = struct.unpack_from("<I", node, 0)[0]
            if not (1 <= nkey <= 64):
                continue
            fp.seek(off + root + 4)
            keys = fp.read(nkey)
            good = sum(1 for b in keys if 0x20 <= b < 0x7F or b >= 0x80)
            if good < max(1, nkey - 2):
                continue
            n_probe += 1
            fp.seek(off)
            data = fp.read(size)
            if not looks_like_mes(data):
                continue
            n_mes += 1
            tag = f"lba{lba:06d}_sz{size}_slot{slot}"
            nlines = dump_mes_file(data, TEXT_OUT / f"{tag}.txt", MES_OUT / f"{tag}.bin")
            keys = [k.decode("latin1", "replace") for k, _ in walk_trie(data)]
            sample = keys[:8]
            mes_index.append((lba, size, slot, flags, nlines, len(keys), ",".join(sample)))
            for key, strs in walk_trie(data):
                k = key.decode("latin1", "replace")
                for i, raw in enumerate(strs):
                    jp = decode_string(raw)
                    sid = k if len(strs) == 1 else f"{k}#{i}"
                    catalog.append((sid, jp, tag))

    print(f"mes files on disc: {n_mes}")
    print("head magics", magics.most_common(12))
    (OUT / "mes_file_index.csv").write_text(
        "lba,size,slot,flags,lines,keys,sample_keys\n"
        + "\n".join(
            f"{lba},{size},{slot},{flags},{nlines},{nkeys},{sample}"
            for lba, size, slot, flags, nlines, nkeys, sample in mes_index
        )
        + "\n",
        encoding="utf-8",
    )

    old_rows = load_rows()
    old_zh: dict[str, str] = {}
    old_kind: dict[str, str] = {}
    for row in old_rows:
        old_zh[row["id"]] = row.get("zh") or ""
        old_kind[row["id"]] = row.get("kind") or ""

    seen: set[str] = set()
    out_rows: list[dict[str, str]] = []
    for sid, jp, notes in catalog:
        if sid in seen:
            continue
        seen.add(sid)
        out_rows.append(
            {
                "id": sid,
                "jp": jp,
                "zh": old_zh.get(sid, ""),
                "notes": notes,
                "kind": old_kind.get(sid) or classify(sid, jp),
            }
        )
    out_rows = preserve_extra_rows(old_rows, out_rows)
    save_rows(out_rows)
    print(
        f"catalog {len(out_rows)} unique ids -> {CATALOG_DIR} "
        f"(kept zh {sum(1 for v in old_zh.values() if v.strip())})"
    )

    # also a readable all-in-one dump
    all_txt = TEXT_OUT / "ALL_DECODED.txt"
    with all_txt.open("w", encoding="utf-8") as f:
        cur = None
        for sid, jp, notes in catalog:
            if notes != cur:
                f.write(f"\n\n======== {notes} ========\n")
                cur = notes
            f.write(f"{sid}\t{jp}\n")
    print("wrote", all_txt)


if __name__ == "__main__":
    main()
