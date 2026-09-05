#!/usr/bin/env python3
"""Dump KIWI fonts from a PCSX2 eeMemory.bin savestate.

KIWI header (64 bytes), then:
  u32 palette[field16]
  bitmap bank0[field32]   # 4bpp, width*height/2 bytes each; codes 0 .. n0-1
  bitmap bank1[field34]   # codes 192 .. 192+n1-1
  u8 metrics0[n0][2]
  u8 metrics1[n1][2]

Relocated RAM objects store pointers at +64/+68/+72/+76/+80 instead of
in-file offsets. Magic is b'KIWI', version 17.
"""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image, ImageDraw


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def parse_header(buf: bytes, loc: int = 0) -> dict:
    if buf[loc : loc + 4] != b"KIWI":
        raise ValueError("not KIWI")
    return {
        "loc": loc,
        "ver": u32(buf, loc + 4),
        "w": u16(buf, loc + 8),
        "h": u16(buf, loc + 10),
        "bpp_field": u16(buf, loc + 12),
        "f14": u16(buf, loc + 14),
        "pal_n": u32(buf, loc + 16),
        "n0": u16(buf, loc + 32),
        "n1": u16(buf, loc + 34),
        "pal": u32(buf, loc + 64),
        "bmp0": u32(buf, loc + 68),
        "bmp1": u32(buf, loc + 72),
        "met0": u32(buf, loc + 76),
        "met1": u32(buf, loc + 80),
    }


def bytes_per_glyph(w: int, h: int, bpp_field: int) -> int:
    if bpp_field == 8:
        return w * h
    return (w * h) // 2  # 4bpp


def decode_glyph(data: bytes, w: int, h: int, bpp_field: int) -> Image.Image:
    img = Image.new("L", (w, h), 0)
    px = img.load()
    k = 0
    if bpp_field == 8:
        for y in range(h):
            for x in range(w):
                if k < len(data):
                    px[x, y] = data[k]
                    k += 1
        return img
    for y in range(h):
        x = 0
        while x < w:
            b = data[k] if k < len(data) else 0
            k += 1
            px[x, y] = (b & 0xF) * 17
            if x + 1 < w:
                px[x + 1, y] = ((b >> 4) & 0xF) * 17
            x += 2
    return img


def sheet_from_bank(
    ram: bytes, bmp: int, n: int, w: int, h: int, bpg: int, bpp: int, code0: int
) -> Image.Image:
    cols = 16
    rows = (n + cols - 1) // cols
    scale = 2 if w >= 16 else 3
    cell = w * scale + 4
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 12)), (16, 16, 16))
    dr = ImageDraw.Draw(sheet)
    for i in range(n):
        g = decode_glyph(ram[bmp + i * bpg : bmp + (i + 1) * bpg], w, h, bpp)
        g = g.resize((w * scale, h * scale), Image.NEAREST).convert("RGB")
        x, y = (i % cols) * cell, (i // cols) * (cell + 12)
        sheet.paste(g, (x + 2, y + 2))
        dr.text((x + 2, y + h * scale + 2), str(code0 + i), fill=(180, 180, 80))
    return sheet


def find_kiwi_objects(ram: bytes) -> list[int]:
    locs = []
    i = 0
    while True:
        j = ram.find(b"KIWI", i)
        if j < 0:
            break
        if j + 8 <= len(ram) and u32(ram, j + 4) == 17:
            w, h = u16(ram, j + 8), u16(ram, j + 10)
            if 8 <= w <= 64 and 8 <= h <= 64:
                locs.append(j)
        i = j + 4
    return locs


def dump_ram_fonts(ram_path: Path, out_dir: Path) -> None:
    ram = ram_path.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    locs = find_kiwi_objects(ram)
    # keep relocated copies (pointers look like EE RAM)
    relocated = []
    for loc in locs:
        h = parse_header(ram, loc)
        if 0x100000 < h["bmp0"] < 0x2000000:
            relocated.append(h)
    # unique by (w,h,n0,n1)
    seen = set()
    uniq = []
    for h in relocated:
        key = (h["w"], h["h"], h["n0"], h["n1"], h["bpp_field"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(h)
    for h in uniq:
        bpg = bytes_per_glyph(h["w"], h["h"], h["bpp_field"])
        name = f"kiwi_{h['w']}x{h['h']}_n{h['n0']}+{h['n1']}_bpp{h['bpp_field']}"
        print(name, "at", hex(h["loc"]))
        if h["n0"] and h["bmp0"] > 0x1000:
            sheet_from_bank(
                ram, h["bmp0"], h["n0"], h["w"], h["h"], bpg, h["bpp_field"], 0
            ).save(out_dir / f"{name}_bank0.png")
        if h["n1"] and h["bmp1"] > 0x1000:
            # page the large kanji bank
            page = 512
            for start in range(0, h["n1"], page):
                n = min(page, h["n1"] - start)
                sheet_from_bank(
                    ram,
                    h["bmp1"] + start * bpg,
                    n,
                    h["w"],
                    h["h"],
                    bpg,
                    h["bpp_field"],
                    192 + start,
                ).save(out_dir / f"{name}_bank1_{192+start:04d}.png")


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    dump_ram_fonts(
        repo / "extracted" / "ram" / "eeMemory.bin",
        repo / "extracted" / "font" / "kiwi_atlas",
    )
