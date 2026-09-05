#!/usr/bin/env python3
"""Patch the Hanjuku Hero 4 ISO: ELF 2-byte font decoder, 16x16 + 12x12 KIWI,
and recoded mes strings.

Font pack slot 49: indices 0–1 (16x16 main + medium) and 2–3 (12x12)
are replaced with the full Chinese cmap (n1=2760). Index 4 (8bpp)
and 5 (16x16 subset) stay stock.
"""
from __future__ import annotations

import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lzss import lzss_compress, lzss_decompress  # noqa: E402
from mes_codec import (  # noqa: E402
    decode_font_codes,
    encode_merged,
    encode_token,
    encode_tokens,
    pack_trie,
    walk_trie,
)
from zh_csv import keep_raw, kinds_by_id, load_cmap, zh_by_id  # noqa: E402

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


def main() -> None:
    fonts_only = "--fonts-only" in sys.argv
    if fonts_only:
        print("fonts-only: skip mes recode")
    else:
        cmap = load_cmap()
        catalog = zh_by_id()
        kinds = kinds_by_id()
        print(f"cmap {len(cmap)}  catalog zh {sum(1 for v in catalog.values() if v.strip())}")

        for g in list(range(0, 192, 17)) + [192, 250, 494, 1000, 192 + 2759]:
            raw = encode_token(g, mul48=True)
            back = decode_font_codes(raw + b"\x00", font_max=12000, mul48=True)
            if back != [g]:
                raise SystemExit(f"encode roundtrip fail {g} -> {back} raw={raw.hex()}")
        print("glyph encode roundtrip ok")

    elf = bytearray(ELF_EXTRACTED.read_bytes())
    patch_decoder(elf)

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
