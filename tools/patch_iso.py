#!/usr/bin/env python3
"""Patch the Hanjuku Hero 4 ISO: ELF 2-byte font decoder, 16x16 + 12x12 KIWI,
recode mes, and recode VFS slot 0 hero/kingdom instance names.

Font pack slot 49: indices 0–1 (16x16 main + medium) and 2–3 (12x12)
are replaced with the full Chinese cmap (n1=2760). Index 4 (8bpp)
and 5 (16x16 subset) stay stock.

Flags: --fonts-only, --slot0-names-only, --allow-pcsx2
"""
from __future__ import annotations

import csv
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lzss import lzss_compress, lzss_decompress  # noqa: E402
from mes_codec import (  # noqa: E402
    HIRA,
    MissingGlyphs,
    decode_font_codes,
    encode_merged,
    encode_token,
    encode_tokens,
    pack_trie,
    walk_trie,
)
from zh_csv import (  # noqa: E402
    classify,
    keep_raw,
    kinds_by_id,
    load_cmap,
    load_rows,
    missing_cmap_chars,
    zh_by_id,
)

ROOT = Path(__file__).resolve().parent.parent
ISO = ROOT / "半熟英雄4-7人的半熟英雄.iso"
ELF_EXTRACTED = ROOT / "extracted/SLPM_658.39"
KIWI_BIN = ROOT / "extracted/font/zh/kiwi_16x16.bin"
KIWI12_BIN = ROOT / "extracted/font/zh/kiwi_12x12.bin"
MES_INDEX = ROOT / "extracted/mes_file_index.csv"
MES_DIR = ROOT / "extracted/mes"

LOAD_V = 0x210000
LOAD_FILE = 0x1000
TABLE_VA = 0x432C48
TABLE_N = 19967
SECTOR = 2048
FONT_SLOT = 49
F7_MAGIC = 0x19283746
ELF_LBA = 931018

# 2-byte path at 0x2dbdb8..0x2dbdfc.
# Stock issues a dummy `mult v0,35` (second byte) then `mult a0,48` but
# adds a0 (delta-1), never LO. Turning on *48 via mflo was too close to
# those multiplys; a later ALU *48 still mis-decoded until the 35-mult
# was removed (PCSX2 rec / HI-LO clash). A mis-encoded addu $s0 also
# clobbered the string cursor so only the first glyph survived.
#
# Working sequence: nop the 35-mult, compute (delta-1)*48 with shifts,
# q-16 + that, keep the low 16 bits in a1.
DECODER_VA = 0x2DBDB8
DECODER_LEN = 72
# bytes 8..36 (andi through addiu a0,-1) must stay stock
DECODER_MID = bytes.fromhex(
    "ff004230 03004614 01001026 02000010 23100200 23104600 ff004230 ffff4424"
)
DECODER_NEW = (
    bytes.fromhex("00000000 00000000")  # nop dummy addiu 35 + mult v0,35
    + DECODER_MID
    + bytes.fromhex("00000000")  # nop dummy addiu 48
    + bytes.fromhex("40190400 00210400 21208300 82100500 f0ff4224 21104400 ffff4530")
)
DECODER_OLD = DECODER_NEW  # unused alias


def fo(va: int) -> int:
    return va - LOAD_V + LOAD_FILE


def kiwi_ondisk(blob: bytes) -> bytes:
    """Drop the 20-byte pointer table our builder inserts after the 64-byte header."""
    if blob[:4] != b"KIWI":
        raise ValueError("not KIWI")
    n1 = struct.unpack_from("<H", blob, 34)[0]
    n0 = struct.unpack_from("<H", blob, 32)[0]
    pal_n = struct.unpack_from("<I", blob, 16)[0]
    w, h, bpp = struct.unpack_from("<HHH", blob, 8)
    bpg = w * h if bpp == 8 else (w * h) // 2
    sequential = 64 + pal_n * 4 + n0 * bpg + n1 * bpg + n0 * 2 + n1 * 2
    if len(blob) == sequential:
        return blob
    if len(blob) == sequential + 20:
        return blob[:64] + blob[84:]
    raise ValueError(f"unexpected KIWI size {len(blob)} (want {sequential} or +20)")


def parse_dir_entry(raw: bytes) -> dict:
    b = list(raw)
    off24 = (b[0] << 16) | (b[2] << 8) | b[5]
    size = (b[3] << 16) | (b[7] << 8) | b[4]
    return {
        "off": off24 << 3,
        "t1": b[1],
        "key": b[6] & 0xF8,
        "size": size,
        "n": 1024 + sum(b),
        "raw": raw,
    }


def decrypt_sub(blob: bytes, ent: dict) -> bytes:
    data = bytearray(blob[ent["off"] : ent["off"] + ent["size"]])
    n = min(ent["n"], ent["size"], len(data))
    t1, key = ent["t1"], ent["key"]
    if t1 == 0 and key == 0:
        return bytes(data)
    for i in range(n):
        data[i] = ((data[i] ^ key) - t1) & 0xFF
    return bytes(data)


def encrypt_sub(plain: bytes, ent: dict) -> bytes:
    """Inverse of decrypt_sub on a extracted subfile (not the parent blob)."""
    data = bytearray(plain)
    n = min(ent["n"], ent["size"], len(data))
    t1, key = ent["t1"], ent["key"]
    if t1 == 0 and key == 0:
        return bytes(data)
    for i in range(n):
        data[i] = ((data[i] + t1) ^ key) & 0xFF
    return bytes(data)


def make_dir_entry(off: int, size: int) -> bytes:
    if off & 7:
        raise ValueError("offset not 8-aligned")
    off24 = off >> 3
    return bytes(
        (
            (off24 >> 16) & 0xFF,
            0,
            (off24 >> 8) & 0xFF,
            (size >> 16) & 0xFF,
            size & 0xFF,
            off24 & 0xFF,
            0,
            (size >> 8) & 0xFF,
        )
    )


def extract_fonts(pack: bytes) -> list[bytes]:
    magic = struct.unpack_from("<I", pack, 0)[0]
    if magic != F7_MAGIC:
        raise ValueError(f"slot 49 magic {magic:#x}")
    blob = lzss_decompress(pack[4:])
    fonts = []
    for i in range(6):
        ent = parse_dir_entry(blob[i * 8 : i * 8 + 8])
        fonts.append(decrypt_sub(blob, ent))
    return fonts


def rebuild_font_pack(fonts: list[bytes]) -> bytes:
    n = len(fonts)
    dir_bytes = 8 * n
    pos = (dir_bytes + 15) & ~7
    if pos < 64:
        pos = 64
    chunks = []
    entries = []
    for f in fonts:
        entries.append(make_dir_entry(pos, len(f)))
        chunks.append((pos, f))
        pos = (pos + len(f) + 7) & ~7
    blob = bytearray(pos)
    for i, e in enumerate(entries):
        blob[i * 8 : i * 8 + 8] = e
    for off, f in chunks:
        blob[off : off + len(f)] = f
    inner = lzss_compress(bytes(blob))
    return struct.pack("<I", F7_MAGIC) + inner


def transcode_raw(raw: bytes) -> bytes:
    """Keep glyph ids / controls, rewrite 2-byte codes for the mflo patch."""
    return encode_tokens(decode_font_codes(raw, mul48=False), mul48=True)


def rebuild_mes_file(
    orig: bytes,
    catalog: dict[str, str],
    cmap: dict[str, int],
    kinds: dict[str, str],
) -> bytes:
    rows = walk_trie(orig)
    out: list[tuple[bytes, list[bytes]]] = []
    for key, strs in rows:
        k = key.decode("latin1", "replace")
        new_strs = []
        for i, raw in enumerate(strs):
            sid = k if len(strs) == 1 else f"{k}#{i}"
            zh = catalog.get(sid) or ""
            if zh.strip() and not keep_raw(sid, kinds.get(sid, "")):
                try:
                    new_strs.append(encode_merged(raw, zh, cmap, mul48=True))
                except MissingGlyphs:
                    raise
                except ValueError:
                    new_strs.append(transcode_raw(raw))
            else:
                new_strs.append(transcode_raw(raw))
        out.append((key, new_strs))
    return pack_trie(out)


def patch_decoder(elf: bytearray) -> None:
    off = fo(DECODER_VA)
    mid = bytes(elf[off + 8 : off + 8 + len(DECODER_MID)])
    if mid != DECODER_MID:
        raise SystemExit(f"decoder mid mismatch at {off + 8:#x}: {mid.hex()}")
    cur = bytes(elf[off : off + DECODER_LEN])
    if cur == DECODER_NEW:
        print("decoder already patched")
        return
    elf[off : off + DECODER_LEN] = DECODER_NEW
    print(f"patched decoder at ELF+{off:#x} ({DECODER_LEN} bytes, nop 35-mult + alu*48)")


def _encode_zh(cmap: dict[str, int], text: str) -> bytes:
    toks = []
    for ch in text:
        g = cmap.get(ch)
        if g is None:
            raise SystemExit(f"embedded name {text!r}: {ch!r} not in cmap")
        toks.append(g)
    return encode_tokens(toks, mul48=True)


def _replace_field(elf: bytearray, old: bytes, new: bytes, *, label: str) -> int:
    """Replace NUL-terminated `old` with `new` where the field has room."""
    n = 0
    start = 0
    while True:
        i = elf.find(old, start)
        if i < 0:
            break
        # Field is old + trailing NULs up to the next nonzero (cap 24).
        j = i + len(old)
        while j < len(elf) and elf[j] == 0 and j - i < 24:
            j += 1
        room = j - i
        if len(new) >= room:
            print(f"skip {label} at ELF+{i:#x}: need {len(new)}+NUL, room {room}")
            start = i + 1
            continue
        elf[i : i + len(new)] = new
        elf[i + len(new) : i + room] = b"\x00" * (room - len(new))
        n += 1
        start = i + room
    print(f"embedded {label}: {n}")
    return n


# Same wrappers as the generals name table / mes PrintMes.
NAME_PREFIX = ("C", 10, 91)
NAME_SUFFIX = ("C", 2, None)

# PrintMes entry (a2 = font-coded string). Do not hook this: a code cave in
# libcdvd .data at 0x42E120 hangs (jal) or crashes PCSX2 (j → TLB 0x10 /
# unaligned PC 0x3c088889). Encodings below are still used if we recode
# instance RAM at spawn.
DECODER_FN_VA = 0x2DB990
NAME_REMAP_VA = 0x42E120
NAME_REMAP_TABLE_OFF = 0x180
NAME_REMAP_ENTRY = 36
# Old 2-byte 「星」 (glyph 195) as written by the stock encoder; the
# patched ×48 decoder reads it as 啊 (289).
KINGDOM_STAR_OLD = bytes.fromhex("9497")
# 宝瓶首都节点 is 「アクエリアスの初」, not 「…星」. Tail is の初 in stock encoding.
KINGDOM_INIT_OLD = bytes.fromhex("350cfa")
# Wipe enough of the unused PrintMes remap cave (table is no longer written).
NAME_REMAP_MAX_PAIRS = 16

# ELF default general names: id → stock JP encoding (zh comes from instance.csv).
ELF_NAME_NEEDLES = (
    ("inst_elf_cocott", bytes.fromhex("696919fa")),
    ("inst_elf_alfalfa", bytes.fromhex("6d0561d70561d7")),
)


def patch_embedded_names(elf: bytearray, cmap: dict[str, int]) -> None:
    """Recode ELF default unit names and debug ポッキリ strings.

    Default generals sit at file 0x20c1a0 (VA 0x41B1A0), stride 0x80.
    Weekday-hero / planet titles are in VFS slot 0 (instance.csv), not here.
    """
    by_id = {r["id"]: r for r in load_rows()}
    for sid, old in ELF_NAME_NEEDLES:
        row = by_id.get(sid) or {}
        zh = (row.get("zh") or "").strip()
        jp = (row.get("jp") or "").strip() or sid
        if not zh or zh == jp:
            print(f"embedded {sid}: skip (no zh)")
            continue
        _replace_field(elf, old, _encode_zh(cmap, zh), label=f"{jp}→{zh}")

    pok_raw = bytes.fromhex("9d1915db")
    pok_zh = _encode_zh(cmap, "波奇利")
    n_pok = 0
    start = 0
    while True:
        i = elf.find(pok_raw, start)
        if i < 0:
            break
        wrapped = i >= 2 and bytes(elf[i - 2 : i]) == bytes.fromhex("48a3")
        if wrapped:
            new = (
                encode_tokens([NAME_PREFIX], mul48=True)
                + pok_zh
                + encode_token(NAME_SUFFIX, mul48=True)
            )
            field = i - 2
        else:
            new = pok_zh
            field = i
        orig_end = i + len(pok_raw)
        while orig_end < len(elf) and elf[orig_end] != 0:
            orig_end += 1
        room = orig_end - field + 1
        if len(new) < room:
            elf[field : field + len(new)] = new
            elf[field + len(new) : field + room] = b"\x00" * (room - len(new))
            n_pok += 1
            start = field + room
        else:
            print(f"skip ポッキリ at ELF+{i:#x}: need {len(new)}+NUL, room {room}")
            start = i + 1
    print(f"embedded ポッキリ→波奇利: {n_pok}")


def _kana_glyph(ch: str) -> int:
    if ch == "ー":
        return 85
    if ch in "ッっ":
        return 87
    o = ord(ch)
    if 0x30A1 <= o <= 0x30F6:
        hira = chr(o - 0x60)
        for i, h in enumerate(HIRA):
            if h == hira:
                return 90 + i
        raise ValueError(f"no kana glyph for {ch!r}")
    raise ValueError(f"not katakana: {ch!r}")


def _leading_katakana(s: str) -> str:
    out: list[str] = []
    for ch in s:
        o = ord(ch)
        if ch == "ー" or ch in "ッっ" or 0x30A1 <= o <= 0x30F6:
            out.append(ch)
        else:
            break
    return "".join(out)


def _hud_name_entries(cmap: dict[str, int]) -> list[tuple[bytes, bytes]]:
    """Build (old, new) encodings from instance.csv; zh is never hardcoded."""
    out: list[tuple[bytes, bytes]] = []
    n_named = 0
    for row in load_rows():
        sid = row.get("id") or ""
        if not sid.startswith("inst_"):
            continue
        kind = row.get("kind") or classify(sid, row.get("jp") or "")
        if kind not in ("hero", "planet", "planet_init"):
            continue
        jp = (row.get("jp") or "").strip()
        zh = (row.get("zh") or "").strip()
        if not jp:
            raise SystemExit(f"{sid}: empty jp")
        if not zh or zh == jp:
            print(f"instance {sid}: skip (no zh)")
            continue
        n_named += 1
        if kind == "hero":
            glyphs = [_kana_glyph(ch) for ch in jp]
            old = encode_tokens([NAME_PREFIX, *glyphs, NAME_SUFFIX], mul48=True)
            new = encode_tokens(
                [NAME_PREFIX, *[_zh_glyph(cmap, ch) for ch in zh], NAME_SUFFIX],
                mul48=True,
            )
        elif kind == "planet_init":
            kana = _leading_katakana(jp)
            if not kana:
                raise SystemExit(f"{sid}: jp has no leading katakana")
            old = encode_tokens([_kana_glyph(ch) for ch in kana], mul48=True) + KINGDOM_INIT_OLD
            new = encode_tokens([_zh_glyph(cmap, ch) for ch in zh], mul48=True)
        else:
            glyphs = [_kana_glyph(ch) for ch in jp]
            old = encode_tokens(glyphs, mul48=True) + KINGDOM_STAR_OLD
            new = encode_tokens([_zh_glyph(cmap, ch) for ch in zh], mul48=True)
        if not old or not new or len(old) > 32 or len(new) > 32:
            raise SystemExit(f"{sid} {jp}->{zh}: old={len(old)} new={len(new)}")
        out.append((old, new))
    if n_named == 0:
        raise SystemExit("instance.csv has no inst_hero_/inst_planet_ zh")
    out.sort(key=lambda p: len(p[0]), reverse=True)
    return out


def _zh_glyph(cmap: dict[str, int], ch: str) -> int:
    g = cmap.get(ch)
    if g is None:
        raise SystemExit(f"HUD name {ch!r} not in cmap")
    return g


def _i_ins(op: int, rs: int, rt: int, imm: int) -> int:
    return (op << 26) | (rs << 21) | (rt << 16) | (imm & 0xFFFF)


def _r_ins(fn: int, rd: int, rs: int, rt: int, sa: int = 0) -> int:
    return (rs << 21) | (rt << 16) | (rd << 11) | (sa << 6) | fn


def _j_ins(target: int) -> int:
    return (2 << 26) | ((target >> 2) & 0x3FFFFFF)


def _assemble_remap(base_va: int, table_va: int, n_entries: int) -> bytes:
    """MIPS: rewrite a2's font string if it matches a HUD name table entry.

    Replaces PrintMes's first instruction (addiu sp,-64). Must be entered with
    `j`, never `jal`: PrintMes saves ra at +0x14, so jal would make every
    PrintMes return to itself and hang before the title can finish.

    Delay slot of the hook already copied a1→t0; t0 is restored, then `j`
    back to PrintMes+8. Match at offset 0 and +4 (kingdom names after 18011801).
    """
    z, v0, v1 = 0, 2, 3
    a1, a2 = 5, 6
    t0, t1, t2, t3, t4, t5, t6, t7, t8, t9 = 8, 9, 10, 11, 12, 13, 14, 15, 24, 25
    sp = 29
    ADDIU, BEQ, BNE, LUI, LBU, SB = 9, 4, 5, 15, 0x24, 0x28
    ADDU, SUBU, OR, SLTI, DADDU = 0x21, 0x23, 0x25, 0x0A, 0x2D
    ret_va = DECODER_FN_VA + 8

    lo = table_va & 0xFFFF
    hi = ((table_va + 0x8000) >> 16) & 0xFFFF
    ops: list = [
        ("addiu", sp, sp, -64),
        ("beq", a2, z, "exit"),
        ("nop",),
        ("lui", t1, hi),
        ("addiu", t1, t1, lo),
        ("addiu", t9, z, n_entries),
        ("label", "next_entry"),
        ("beq", t9, z, "exit"),
        ("nop",),
        ("lbu", t2, t1, 0),
        ("lbu", t3, t1, 1),
        ("addiu", t4, t1, 4),
        ("addiu", t5, z, 0),
        ("label", "try_off"),
        ("addu", t6, a2, t5),
        ("or", t7, t2, t2),
        ("or", t8, t6, t6),
        ("or", v1, t4, t4),
        ("label", "cmp"),
        ("beq", t7, z, "matched"),
        ("nop",),
        ("lbu", v0, t8, 0),
        ("lbu", t0, v1, 0),
        ("bne", v0, t0, "next_off"),
        ("addiu", t8, t8, 1),
        ("addiu", v1, v1, 1),
        ("addiu", t7, t7, -1),
        ("beq", z, z, "cmp"),
        ("nop",),
        ("label", "next_off"),
        ("bne", t5, z, "advance"),
        ("nop",),
        ("addiu", t5, z, 4),
        ("beq", z, z, "try_off"),
        ("nop",),
        ("label", "advance"),
        ("addiu", t1, t1, NAME_REMAP_ENTRY),
        ("addiu", t9, t9, -1),
        ("beq", z, z, "next_entry"),
        ("nop",),
        ("label", "matched"),
        ("addu", t6, a2, t5),
        ("addiu", t8, t1, 20),
        ("or", t7, t3, t3),
        ("label", "cpy"),
        ("beq", t7, z, "zfill"),
        ("nop",),
        ("lbu", v0, t8, 0),
        ("addiu", t8, t8, 1),
        ("sb", v0, t6, 0),
        ("addiu", t6, t6, 1),
        ("addiu", t7, t7, -1),
        ("beq", z, z, "cpy"),
        ("nop",),
        ("label", "zfill"),
        ("subu", t7, t2, t3),
        ("slti", t0, t7, 1),
        ("bne", t0, z, "exit"),
        ("nop",),
        ("label", "zf"),
        ("sb", z, t6, 0),
        ("addiu", t6, t6, 1),
        ("addiu", t7, t7, -1),
        ("bne", t7, z, "zf"),
        ("nop",),
        ("label", "exit"),
        ("daddu", t0, a1, z),
        ("j", ret_va),
        ("nop",),
    ]

    labels: dict[str, int] = {}
    words: list[object] = []
    for op in ops:
        if op[0] == "label":
            labels[op[1]] = len(words)
            continue
        words.append(op)

    def rel(idx: int, lab: str) -> int:
        tgt = labels[lab]
        return tgt - (idx + 1)

    out = bytearray()
    for i, op in enumerate(words):
        k = op[0]
        pc = base_va + i * 4
        if k == "nop":
            w = 0
        elif k == "addiu":
            w = _i_ins(ADDIU, op[2], op[1], op[3])
        elif k == "lui":
            w = _i_ins(LUI, 0, op[1], op[2])
        elif k == "lbu":
            w = _i_ins(LBU, op[2], op[1], op[3])
        elif k == "sb":
            w = _i_ins(SB, op[2], op[1], op[3])
        elif k == "beq":
            w = _i_ins(BEQ, op[1], op[2], rel(i, op[3]))
        elif k == "bne":
            w = _i_ins(BNE, op[1], op[2], rel(i, op[3]))
        elif k == "addu":
            w = _r_ins(ADDU, op[1], op[2], op[3])
        elif k == "subu":
            w = _r_ins(SUBU, op[1], op[2], op[3])
        elif k == "or":
            w = _r_ins(OR, op[1], op[2], op[3])
        elif k == "daddu":
            w = _r_ins(DADDU, op[1], op[2], op[3])
        elif k == "slti":
            w = _i_ins(SLTI, op[2], op[1], op[3])
        elif k == "j":
            tgt = op[1]
            if (tgt & 0xF0000000) != (pc & 0xF0000000):
                raise SystemExit(f"j {tgt:#x} crosses 256MB from {pc:#x}")
            w = _j_ins(tgt)
        else:
            raise SystemExit(f"unknown mips op {op}")
        # sanity: beq/bne offset fits s16
        if k in ("beq", "bne") and not -32768 <= rel(i, op[3]) <= 32767:
            raise SystemExit(f"branch too far at {pc:#x}")
        out += struct.pack("<I", w)
        _ = pc
    return bytes(out)


def _pack_remap_table(entries: list[tuple[bytes, bytes]]) -> bytes:
    blob = bytearray()
    for old, new in entries:
        rec = bytearray(NAME_REMAP_ENTRY)
        rec[0] = len(old)
        rec[1] = len(new)
        rec[4 : 4 + len(old)] = old
        rec[20 : 20 + len(new)] = new
        blob += rec
    return bytes(blob)


def patch_hud_name_remap(elf: bytearray, cmap: dict[str, int]) -> None:
    """Keep PrintMes unhooked. cmap is unused (call-site compatibility).

    An earlier hook jumped from PrintMes into libcdvd .data at 0x42E120.
    jal clobbered ra (hang). j reached the stub; PCSX2 then TLB-missed
    loads from 0x10 (one per table entry) and died on an unaligned jump
    to 0x3c088889. Live RAM pokes already proved the encodings; recode
    names at instance init instead of PrintMes.
    """
    _ = cmap
    stock = 0x27BDFFC0  # addiu sp,sp,-64
    fn_off = fo(DECODER_FN_VA)
    orig = struct.unpack_from("<I", elf, fn_off)[0]
    hop_j = _j_ins(NAME_REMAP_VA)
    hop_jal = (3 << 26) | ((NAME_REMAP_VA >> 2) & 0x3FFFFFF)
    if orig not in (stock, hop_j, hop_jal):
        raise SystemExit(f"PrintMes prologue unexpected {orig:#x}")
    if orig != stock:
        struct.pack_into("<I", elf, fn_off, stock)
        print(f"removed PrintMes HUD hook ({orig:#x} -> addiu sp,-64)")
    else:
        print("PrintMes prologue stock (no HUD hook)")
    cave_off = fo(NAME_REMAP_VA)
    n = NAME_REMAP_TABLE_OFF + NAME_REMAP_MAX_PAIRS * NAME_REMAP_ENTRY
    cave_head = struct.unpack_from("<I", elf, cave_off)[0]
    if orig in (hop_j, hop_jal) or cave_head == stock:
        elf[cave_off : cave_off + n] = b"\x00" * n
        print(f"cleared name-remap cave {NAME_REMAP_VA:#x} ({n} bytes)")


def _replace_in_buf(buf: bytearray, old: bytes, new: bytes) -> int:
    """Overwrite NUL-padded `old` with `new` (needs one extra NUL of room)."""
    n = 0
    start = 0
    while True:
        i = buf.find(old, start)
        if i < 0:
            break
        j = i + len(old)
        while j < len(buf) and buf[j] == 0 and j - i < 32:
            j += 1
        room = j - i
        if len(new) >= room:
            start = i + 1
            continue
        buf[i : i + len(new)] = new
        buf[i + len(new) : i + room] = b"\x00" * (room - len(new))
        n += 1
        start = i + room
    return n


# VFS slot 0 (LBA from hash[0]) is an F7-style directory. Subfiles used at
# new-game init (0x236c48): 0 = 200×64 egg-monsters (name +8, ASCII id +41),
# 1 = 1000×48 skills (5 slots per egg, name +6), 4 = 100-byte units,
# 5 = 7×84 weekday heroes (name at +24), 9 = 518×42 map nodes (title +12).
SLOT0_DIR_INDEXES = (4, 5, 9)
EGG_REC = 64
EGG_NAME_OFF = 8
EGG_ID_OFF = 41
EGG_NAME_ROOM = EGG_ID_OFF - EGG_NAME_OFF
SKILL_REC = 48
SKILL_NAME_OFF = 6
SKILL_NAME_ROOM = SKILL_REC - SKILL_NAME_OFF
SKILL_SLOTS_PER_EGG = 5


def _wrap_zh_name(cmap: dict[str, int], zh: str) -> bytes:
    return encode_tokens(
        [NAME_PREFIX, *[_zh_glyph(cmap, ch) for ch in zh], NAME_SUFFIX],
        mul48=True,
    )


def _write_name_field(buf: bytearray, off: int, raw: bytes, room: int) -> bool:
    if not raw or len(raw) + 1 > room:
        return False
    buf[off : off + len(raw)] = raw
    buf[off + len(raw) : off + room] = b"\x00" * (room - len(raw))
    return True


def _slot0_put_sub(blob: bytearray, ent: dict, plain: bytes) -> None:
    enc = encrypt_sub(plain, ent)
    fake = bytearray(ent["off"] + len(enc))
    fake[ent["off"] : ent["off"] + len(enc)] = enc
    if decrypt_sub(fake, ent) != bytes(plain):
        raise SystemExit("slot0 encrypt roundtrip failed")
    blob[ent["off"] : ent["off"] + ent["size"]] = enc


def _patch_egg_name_table(plain: bytearray, cmap: dict[str, int], zhmap: dict[str, str]) -> int:
    n = 0
    nrec = len(plain) // EGG_REC
    for i in range(nrec):
        base = i * EGG_REC
        rec = plain[base : base + EGG_REC]
        z = rec.find(b"\x00", EGG_ID_OFF)
        if z < 0:
            z = EGG_REC
        gid = bytes(rec[EGG_ID_OFF:z]).decode("ascii", "replace")
        if not gid.startswith("eg_"):
            continue
        zh = (zhmap.get(gid) or "").strip()
        if not zh:
            continue
        new = _wrap_zh_name(cmap, zh)
        cur = bytes(rec[EGG_NAME_OFF : EGG_NAME_OFF + EGG_NAME_ROOM])
        padded = new.ljust(EGG_NAME_ROOM, b"\x00")
        if cur == padded:
            continue
        if not _write_name_field(plain, base + EGG_NAME_OFF, new, EGG_NAME_ROOM):
            print(f"slot0 egg skip {gid}: {zh!r} needs {len(new)}+NUL, room {EGG_NAME_ROOM}")
            continue
        n += 1
    return n


def _patch_egg_skill_table(
    egg_plain: bytes,
    skill_plain: bytearray,
    cmap: dict[str, int],
    zhmap: dict[str, str],
) -> int:
    n = 0
    nrec = len(egg_plain) // EGG_REC
    for i in range(nrec):
        rec = egg_plain[i * EGG_REC : (i + 1) * EGG_REC]
        z = rec.find(b"\x00", EGG_ID_OFF)
        if z < 0:
            z = EGG_REC
        gid = bytes(rec[EGG_ID_OFF:z]).decode("ascii", "replace")
        if not gid.startswith("eg_"):
            continue
        for k in range(SKILL_SLOTS_PER_EGG):
            si = i * SKILL_SLOTS_PER_EGG + k
            off = si * SKILL_REC
            if off + SKILL_REC > len(skill_plain):
                break
            raw = bytes(skill_plain[off + SKILL_NAME_OFF : off + SKILL_REC]).split(b"\x00", 1)[0]
            if not raw:
                continue
            zh = (zhmap.get(f"{gid}_at{k + 1}") or "").strip()
            if not zh:
                continue
            new = _wrap_zh_name(cmap, zh)
            cur = bytes(skill_plain[off + SKILL_NAME_OFF : off + SKILL_REC])
            padded = new.ljust(SKILL_NAME_ROOM, b"\x00")
            if cur == padded:
                continue
            if not _write_name_field(skill_plain, off + SKILL_NAME_OFF, new, SKILL_NAME_ROOM):
                print(
                    f"slot0 skill skip {gid}_at{k + 1}: {zh!r} "
                    f"needs {len(new)}+NUL, room {SKILL_NAME_ROOM}"
                )
                continue
            n += 1
    return n


def patch_slot0_instance_names(fp, elf: bytes, cmap: dict[str, int]) -> None:
    """Recode HUD names in VFS slot 0 (heroes, planets, egg-monsters, skills).

    Those strings are XOR/t1-scrambled on disc, so a raw ISO search misses
    them. The loader (0x362928) decrypts into RAM. Do not hook PrintMes.
    Egg display names use catalog ids such as eg_cl_eggm / eg_cl_eggm_at1.
    """
    lba, packed, _unp = struct.unpack_from("<III", elf, fo(TABLE_VA))
    if lba < 1 or packed < 64:
        raise SystemExit(f"VFS slot 0 looks empty lba={lba} size={packed}")
    blob = bytearray(iso_read(fp, lba, packed))
    entries = _hud_name_entries(cmap)
    zhmap = zh_by_id()
    total = 0
    for idx in SLOT0_DIR_INDEXES:
        ent = parse_dir_entry(bytes(blob[idx * 8 : idx * 8 + 8]))
        if ent["off"] + ent["size"] > len(blob) or ent["size"] < 8:
            print(f"slot0[{idx}] skip bad dir off={ent['off']} size={ent['size']}")
            continue
        plain = bytearray(decrypt_sub(blob, ent))
        n = 0
        for old, new in entries:
            n += _replace_in_buf(plain, old, new)
        if n == 0:
            print(f"slot0[{idx}] no HUD names")
            continue
        _slot0_put_sub(blob, ent, bytes(plain))
        total += n
        print(f"slot0[{idx}] recoded {n} names (off={ent['off']} size={ent['size']})")

    egg_ent = parse_dir_entry(bytes(blob[0:8]))
    skill_ent = parse_dir_entry(bytes(blob[8:16]))
    egg_plain = bytearray(decrypt_sub(blob, egg_ent))
    skill_plain = bytearray(decrypt_sub(blob, skill_ent))
    n_egg = _patch_egg_name_table(egg_plain, cmap, zhmap)
    n_sk = _patch_egg_skill_table(bytes(egg_plain), skill_plain, cmap, zhmap)
    if n_egg:
        _slot0_put_sub(blob, egg_ent, bytes(egg_plain))
        print(f"slot0[0] recoded {n_egg} egg names (off={egg_ent['off']} size={egg_ent['size']})")
    else:
        print("slot0[0] no egg names")
    if n_sk:
        _slot0_put_sub(blob, skill_ent, bytes(skill_plain))
        print(f"slot0[1] recoded {n_sk} egg skills (off={skill_ent['off']} size={skill_ent['size']})")
    else:
        print("slot0[1] no egg skills")
    total += n_egg + n_sk

    if total == 0:
        already = 0
        for idx in SLOT0_DIR_INDEXES:
            ent = parse_dir_entry(bytes(blob[idx * 8 : idx * 8 + 8]))
            if ent["off"] + ent["size"] > len(blob) or ent["size"] < 8:
                continue
            plain = decrypt_sub(blob, ent)
            already += sum(plain.count(new) for _old, new in entries)
        already += _patch_egg_name_table(bytearray(decrypt_sub(blob, egg_ent)), cmap, zhmap)
        if already:
            print(f"slot0 names already recoded; skip")
            return
        raise SystemExit("slot0 HUD/egg names: nothing replaced (directory shifted?)")
    iso_write(fp, lba, bytes(blob), packed)
    print(f"slot0 instance names: {total} replacements, LBA {lba}")


def set_hash(elf: bytearray, slot: int, lba: int, packed: int, unp: int) -> None:
    off = fo(TABLE_VA) + slot * 12
    struct.pack_into("<III", elf, off, lba, packed, unp)


def slots_for_file(
    elf: bytes, slot: int, orig_lba: int, flags: int
) -> list[tuple[int, int]]:
    """Slots to update for one mes/font file (includes aliases)."""
    base = fo(TABLE_VA)
    cur_lba, _, cur_unp = struct.unpack_from("<III", elf, base + slot * 12)
    found: list[tuple[int, int]] = []
    for i in range(TABLE_N):
        a, _b, c = struct.unpack_from("<III", elf, base + i * 12)
        if a == cur_lba or a == orig_lba:
            found.append((i, c))
    if not found:
        found = [(slot, flags if flags is not None else cur_unp)]
    # unique slots
    seen = set()
    out = []
    for s, u in found:
        if s not in seen:
            seen.add(s)
            out.append((s, u))
    return out


def set_hash_all(elf: bytearray, slots: list[tuple[int, int]], lba: int, packed: int) -> None:
    for slot, unp in slots:
        set_hash(elf, slot, lba, packed, unp)


def iso_read(fp, lba: int, size: int) -> bytes:
    fp.seek(lba * SECTOR)
    return fp.read(size)


def iso_write(fp, lba: int, data: bytes, orig_size: int) -> None:
    if len(data) > orig_size:
        raise ValueError(f"payload {len(data)} > room {orig_size}")
    fp.seek(lba * SECTOR)
    fp.write(data)
    if len(data) < orig_size:
        fp.write(b"\x00" * (orig_size - len(data)))


def iso_append(fp, data: bytes) -> tuple[int, int]:
    fp.seek(0, 2)
    pos = fp.tell()
    if pos % SECTOR:
        fp.write(b"\x00" * (SECTOR - pos % SECTOR))
    lba = fp.tell() // SECTOR
    fp.write(data)
    if fp.tell() % SECTOR:
        fp.write(b"\x00" * (SECTOR - fp.tell() % SECTOR))
    return lba, len(data)


def update_pvd_sectors(fp, nsectors: int) -> None:
    fp.seek(16 * SECTOR + 80)
    fp.write(struct.pack("<I", nsectors) + struct.pack(">I", nsectors))


def pcsx2_pids() -> list[str]:
    found: list[str] = []
    for name in ("pcsx2-qt", "pcsx2", "PCSX2"):
        r = subprocess.run(
            ["pgrep", "-x", name],
            capture_output=True,
            text=True,
            check=False,
        )
        found.extend(p for p in r.stdout.split() if p)
    return sorted(set(found))


def stop_pcsx2() -> None:
    """Quit PCSX2 so the ISO is not written while mapped."""
    pids = pcsx2_pids()
    if not pids:
        return
    print("stopping PCSX2 (pid " + ", ".join(pids) + ")")
    for name in ("pcsx2-qt", "pcsx2", "PCSX2"):
        subprocess.run(["pkill", "-x", name], check=False)
    for _ in range(40):
        if not pcsx2_pids():
            print("PCSX2 stopped")
            return
        time.sleep(0.25)
    for name in ("pcsx2-qt", "pcsx2", "PCSX2"):
        subprocess.run(["pkill", "-9", "-x", name], check=False)
    time.sleep(0.5)
    left = pcsx2_pids()
    if left:
        raise SystemExit("could not stop PCSX2 (pid " + ", ".join(left) + ")")
    print("PCSX2 killed")


def main() -> None:
    fonts_only = "--fonts-only" in sys.argv
    slot0_only = "--slot0-names-only" in sys.argv
    if fonts_only and slot0_only:
        raise SystemExit("use only one of --fonts-only / --slot0-names-only")

    if "--allow-pcsx2" in sys.argv:
        if pcsx2_pids():
            print("WARNING: PCSX2 running; writing ISO anyway (--allow-pcsx2)")
    else:
        stop_pcsx2()

    if slot0_only:
        cmap = load_cmap()
        missing = missing_cmap_chars(cmap=cmap)
        if missing:
            sample = "".join(list(missing)[:40])
            raise SystemExit(
                f"cmap missing {len(missing)} chars ({sample}…) — "
                "run python3 tools/rebuild.py first"
            )
        elf = ELF_EXTRACTED.read_bytes()
        with ISO.open("r+b") as fp:
            if iso_read(fp, ELF_LBA, 4) != b"\x7fELF":
                raise SystemExit("ELF LBA does not look like ELF")
            patch_slot0_instance_names(fp, elf, cmap)
        print("slot0-names-only done", ISO)
        return

    if fonts_only:
        print("fonts-only: skip mes recode")
    else:
        cmap = load_cmap()
        catalog = zh_by_id()
        kinds = kinds_by_id()
        print(f"cmap {len(cmap)}  catalog zh {sum(1 for v in catalog.values() if v.strip())}")
        missing = missing_cmap_chars(cmap=cmap)
        if missing:
            sample = "".join(list(missing)[:40])
            raise SystemExit(
                f"cmap missing {len(missing)} chars ({sample}…) — "
                "run python3 tools/rebuild.py (or tools/build_kiwi_font.py first)"
            )

        for g in list(range(0, 192, 17)) + [192, 250, 494, 1000, 192 + 2759]:
            raw = encode_token(g, mul48=True)
            back = decode_font_codes(raw + b"\x00", font_max=12000, mul48=True)
            if back != [g]:
                raise SystemExit(f"encode roundtrip fail {g} -> {back} raw={raw.hex()}")
        print("glyph encode roundtrip ok")

    elf = bytearray(ELF_EXTRACTED.read_bytes())
    patch_decoder(elf)
    if not fonts_only:
        patch_embedded_names(elf, cmap)
        patch_hud_name_remap(elf, cmap)

    with ISO.open("r+b") as fp:
        disc_elf_head = iso_read(fp, ELF_LBA, 4)
        if disc_elf_head != b"\x7fELF":
            raise SystemExit("ELF LBA does not look like ELF")
        disc_dec = iso_read(fp, ELF_LBA, fo(DECODER_VA) + DECODER_LEN)[
            fo(DECODER_VA) : fo(DECODER_VA) + DECODER_LEN
        ]
        disc_mid = disc_dec[8 : 8 + len(DECODER_MID)]
        if disc_mid != DECODER_MID:
            raise SystemExit(f"ISO decoder mid unexpected: {disc_mid.hex()}")

        old_lba, old_packed, old_unp = struct.unpack_from(
            "<III", elf, fo(TABLE_VA) + FONT_SLOT * 12
        )
        pack_in = iso_read(fp, old_lba, old_packed)
        fonts = extract_fonts(pack_in)
        print("original fonts", [f[:4] for f in fonts], [len(f) for f in fonts])
        n0, n1 = struct.unpack_from("<HH", fonts[0], 32)
        print(f"idx0 main 16x16 {n0}+{n1} {len(fonts[0])} bytes")
        n0m, n1m = struct.unpack_from("<HH", fonts[1], 32)
        print(f"idx1 medium 16x16 {n0m}+{n1m} {len(fonts[1])} bytes")
        kiwi16 = kiwi_ondisk(KIWI_BIN.read_bytes())
        n0, n1 = struct.unpack_from("<HH", kiwi16, 32)
        print(f"new 16x16 {n0}+{n1} {len(kiwi16)} bytes")
        fonts[0] = kiwi16
        # Dialogue balloons use idx1; n1 must cover rare CJK (抖=1439, 颤=1512)
        # or they fall back to あ. Truncating to 5 VRAM pages caused that.
        fonts[1] = kiwi16
        n0m, n1m = struct.unpack_from("<HH", fonts[1], 32)
        print(f"new idx1 medium 16x16 {n0m}+{n1m} {len(fonts[1])} bytes")
        kiwi12 = kiwi_ondisk(KIWI12_BIN.read_bytes())
        n0_12, n1_12 = struct.unpack_from("<HH", kiwi12, 32)
        print(f"new 12x12 {n0_12}+{n1_12} {len(kiwi12)} bytes")
        fonts[2] = kiwi12
        fonts[3] = kiwi12
        pack = rebuild_font_pack(fonts)
        print(f"font pack {old_packed} -> {len(pack)}")

        blob = lzss_decompress(pack[4:])
        check = decrypt_sub(blob, parse_dir_entry(blob[0:8]))
        if check[:4] != b"KIWI" or struct.unpack_from("<H", check, 34)[0] != n1:
            raise SystemExit("rebuilt pack does not decrypt to new KIWI")

        font_slots = slots_for_file(elf, FONT_SLOT, old_lba, old_unp)
        if len(pack) <= old_packed:
            iso_write(fp, old_lba, pack, old_packed)
            set_hash_all(elf, font_slots, old_lba, len(pack))
            print(f"font pack in-place LBA {old_lba}")
        else:
            lba, packed = iso_append(fp, pack)
            set_hash_all(elf, font_slots, lba, packed)
            print(f"font pack relocated LBA {old_lba} -> {lba} ({packed} bytes)")

        if fonts_only:
            index = []
        else:
            index = list(csv.DictReader(MES_INDEX.open(encoding="utf-8", newline="")))
        n_ok = n_fail = n_grow = 0
        for row in index:
            lba = int(row["lba"])
            size = int(row["size"])
            slot = int(row["slot"])
            src = MES_DIR / f"lba{lba:06d}_sz{size}_slot{slot}.bin"
            orig = src.read_bytes() if src.exists() else iso_read(fp, lba, size)
            try:
                rebuilt = rebuild_mes_file(orig, catalog, cmap, kinds)
            except Exception as e:
                print("mes fail", src.name, e)
                n_fail += 1
                continue
            orig_keys = {k for k, _ in walk_trie(orig)}
            new_keys = {k for k, _ in walk_trie(rebuilt)}
            if orig_keys != new_keys:
                print("mes key-set mismatch", src.name, len(orig_keys), len(new_keys))
                n_fail += 1
                continue
            mes_slots = slots_for_file(elf, slot, lba, int(row["flags"]))
            if len(rebuilt) <= size:
                iso_write(fp, lba, rebuilt, size)
                set_hash_all(elf, mes_slots, lba, len(rebuilt))
            else:
                new_lba, packed = iso_append(fp, rebuilt)
                set_hash_all(elf, mes_slots, new_lba, packed)
                n_grow += 1
            n_ok += 1
        if not fonts_only:
            print(f"mes patched {n_ok} fail {n_fail} relocated {n_grow}")
            patch_slot0_instance_names(fp, elf, cmap)

        fp.seek(ELF_LBA * SECTOR)
        fp.write(elf)
        fp.seek(0, 2)
        nsectors = (fp.tell() + SECTOR - 1) // SECTOR
        update_pvd_sectors(fp, nsectors)
        print("wrote", ISO, "sectors", nsectors)

    ELF_EXTRACTED.write_bytes(elf)
    print("wrote", ELF_EXTRACTED)


if __name__ == "__main__":
    main()
