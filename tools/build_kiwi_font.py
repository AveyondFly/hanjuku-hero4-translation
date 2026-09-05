#!/usr/bin/env python3
"""Build Chinese KIWI bitmap fonts from Noto Sans CJK SC.

Bank0 (0–191) is copied from the original RAM dump so kana / digits /
合言葉 keep working. Bank1 (192+) is every remaining unique character
in translation_catalog.csv zh, rasterized at the native glyph size.

Writes:
  extracted/zh_cmap.csv
  extracted/font/zh/kiwi_{w}x{h}.bin
  extracted/font/zh/atlas_{w}x{h}.png
  extracted/font/zh/preview.png
"""
from __future__ import annotations

import csv
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kiwi_font import bytes_per_glyph, decode_glyph, parse_header  # noqa: E402
from mes_codec import HIRA, hira_to_kata  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "extracted/translation_catalog.csv"
RAM = ROOT / "extracted/ram/eeMemory.bin"
OUT = ROOT / "extracted/font/zh"
CMAP_PATH = ROOT / "extracted/zh_cmap.csv"

NOTO_BOLD = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
NOTO_REG = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")

# Original 16x16 main font / 12x12 small font in eeMemory.bin
SRC_16 = (16, 16, 192, 1727, 4)
SRC_12 = (12, 12, 192, 123, 4)


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def find_kiwi(ram: bytes, key: tuple[int, int, int, int, int]) -> dict:
    w, h, n0, n1, bpp = key
    start = 0
    while True:
        j = ram.find(b"KIWI", start)
        if j < 0:
            raise LookupError(f"KIWI {key} not in RAM")
        if j + 84 <= len(ram) and u32(ram, j + 4) == 17:
            hdr = parse_header(ram, j)
            if (
                hdr["w"] == w
                and hdr["h"] == h
                and hdr["n0"] == n0
                and hdr["n1"] == n1
                and hdr["bpp_field"] == bpp
                and 0x100000 < hdr["bmp0"] < 0x2000000
            ):
                return hdr
        start = j + 4


def bank0_char_map() -> dict[str, int]:
    """Prefer the lowest original bank0 code for each character."""
    out: dict[str, int] = {}
    for i, ch in enumerate(HIRA):
        if ch and ch not in out:
            out[ch] = i
        kata = hira_to_kata(ch) if ch else ""
        if kata and kata not in out:
            out[kata] = 90 + i
    digits = "1234567890"
    for i, ch in enumerate(digits):
        out[ch] = 180 + i
    out["@"] = 190
    return out


def collect_zh_chars() -> list[str]:
    seen: dict[str, int] = {}
    with CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for ch in row.get("zh") or "":
                seen[ch] = seen.get(ch, 0) + 1
    return sorted(seen, key=lambda c: (-seen[c], c))


def build_cmap(zh_chars: list[str], bank0: dict[str, int]) -> dict[str, int]:
    cmap = dict(bank0)
    next_id = 192
    extras: list[str] = []
    for ch in zh_chars:
        if ch in cmap:
            continue
        if ch in " \t\n\r\u3000":
            continue
        extras.append(ch)
    punct = []
    latin = []
    cjk = []
    other = []
    for ch in extras:
        o = ord(ch)
        if ch.isascii():
            latin.append(ch)
        elif 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF:
            cjk.append(ch)
        elif 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF or o in (0x00B7, 0x2014, 0x2026, 0x25CB, 0x25B3):
            punct.append(ch)
        else:
            other.append(ch)
    for ch in punct + latin + other + cjk:
        cmap[ch] = next_id
        next_id += 1
    return cmap


def encode_glyph(img: Image.Image, w: int, h: int) -> bytes:
    px = img.load()
    out = bytearray()
    for y in range(h):
        x = 0
        while x < w:
            a = min(15, (px[x, y] or 0) // 17)
            b = min(15, (px[x + 1, y] or 0) // 17) if x + 1 < w else 0
            out.append(a | (b << 4))
            x += 2
    return bytes(out)


def render_char(font: ImageFont.FreeTypeFont, ch: str, w: int, h: int) -> Image.Image:
    img = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(img)
    try:
        bbox = dr.textbbox((0, 0), ch, font=font)
    except Exception:
        return img
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    if tw <= 0 or th <= 0:
        return img
    x = (w - tw) // 2 - bbox[0]
    y = (h - th) // 2 - bbox[1]
    # CJK sits a pixel high with Noto; nudge down.
    if "\u4e00" <= ch <= "\u9fff":
        y += 1
    dr.text((x, y), ch, font=font, fill=255)
    return img


def metrics_of(img: Image.Image) -> tuple[int, int]:
    px = img.load()
    w, h = img.size
    xs = [x for y in range(h) for x in range(w) if px[x, y] > 24]
    if not xs:
        return (0, 6)
    left = xs[0] if xs else 0
    left = min(xs)
    right = w - 1 - max(xs)
    return (min(left, 15), min(right, 15))


def load_face(size: int) -> ImageFont.FreeTypeFont:
    path = NOTO_BOLD if NOTO_BOLD.exists() else NOTO_REG
    return ImageFont.truetype(str(path), size, index=0)


def write_kiwi(
    ram: bytes,
    src_key: tuple[int, int, int, int, int],
    cmap: dict[str, int],
    font: ImageFont.FreeTypeFont,
    dest: Path,
) -> dict:
    hdr = find_kiwi(ram, src_key)
    loc = hdr["loc"]
    w, h = hdr["w"], hdr["h"]
    bpp = hdr["bpp_field"]
    n0 = hdr["n0"]
    bpg = bytes_per_glyph(w, h, bpp)
    pal_n = hdr["pal_n"]

    n1 = max(cmap.values()) + 1 - 192
    if n1 < 1:
        n1 = 1

    pal = ram[hdr["pal"] : hdr["pal"] + pal_n * 4]
    bmp0 = ram[hdr["bmp0"] : hdr["bmp0"] + n0 * bpg]
    met0 = ram[hdr["met0"] : hdr["met0"] + n0 * 2]

    id_to_char = {gid: ch for ch, gid in cmap.items()}
    bmp1 = bytearray(n1 * bpg)
    met1 = bytearray(n1 * 2)
    for i in range(n1):
        ch = id_to_char.get(192 + i, "")
        if not ch:
            met1[i * 2 : i * 2 + 2] = bytes((0, 6))
            continue
        img = render_char(font, ch, w, h)
        g = encode_glyph(img, w, h)
        bmp1[i * bpg : i * bpg + bpg] = g
        a, b = metrics_of(img)
        met1[i * 2] = a
        met1[i * 2 + 1] = b

    header = bytearray(ram[loc : loc + 64])
    struct.pack_into("<H", header, 34, n1)

    pal_off = 84
    bmp0_off = pal_off + len(pal)
    bmp1_off = bmp0_off + len(bmp0)
    met0_off = bmp1_off + len(bmp1)
    met1_off = met0_off + len(met0)
    ptrs = struct.pack("<IIIII", pal_off, bmp0_off, bmp1_off, met0_off, met1_off)
    blob = bytes(header) + ptrs + pal + bmp0 + bytes(bmp1) + met0 + bytes(met1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return {"w": w, "h": h, "n0": n0, "n1": n1, "bytes": len(blob), "bpg": bpg, "hdr": hdr}


def atlas(blob: bytes, cmap: dict[str, int], dest: Path, show: int = 96) -> None:
    """Small bank1 sample sheet. Keep it tiny so it can be opened in-session."""
    w = struct.unpack_from("<H", blob, 8)[0]
    h = struct.unpack_from("<H", blob, 10)[0]
    bpp = struct.unpack_from("<H", blob, 12)[0]
    n1 = struct.unpack_from("<H", blob, 34)[0]
    bmp1_off = struct.unpack_from("<I", blob, 72)[0]
    bpg = bytes_per_glyph(w, h, bpp)
    id_to_char = {gid: ch for ch, gid in cmap.items()}
    cols = 16
    show = min(n1, show)
    rows = (show + cols - 1) // cols
    scale = 2
    cell = w * scale + 2
    sheet = Image.new("RGB", (cols * cell, rows * (cell + 10)), (16, 16, 16))
    dr = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default()
    for i in range(show):
        raw = blob[bmp1_off + i * bpg : bmp1_off + (i + 1) * bpg]
        g = decode_glyph(raw, w, h, bpp).resize((w * scale, h * scale), Image.NEAREST).convert("RGB")
        x, y = (i % cols) * cell, (i // cols) * (cell + 10)
        sheet.paste(g, (x + 1, y + 1))
        ch = id_to_char.get(192 + i, "")
        dr.text((x + 1, y + h * scale + 1), ch or "·", font=label_font, fill=(180, 180, 80))
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)


def preview_line(font: ImageFont.FreeTypeFont, text: str, w: int, h: int, dest: Path) -> None:
    imgs = [render_char(font, ch, w, h) for ch in text]
    sheet = Image.new("L", (w * len(imgs) + 8, h + 8), 0)
    x = 4
    for im in imgs:
        sheet.paste(im, (x, 4))
        x += w
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(dest)


def write_cmap(cmap: dict[str, int], path: Path) -> None:
    rows = sorted(cmap.items(), key=lambda kv: kv[1])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["char", "hex", "glyph"])
        for ch, gid in rows:
            w.writerow([ch, f"U+{ord(ch):04X}", gid])


def main() -> None:
    ram = RAM.read_bytes()
    bank0 = bank0_char_map()
    zh_chars = collect_zh_chars()
    cmap = build_cmap(zh_chars, bank0)
    n1 = max(g for g in cmap.values() if g >= 192) - 191
    cjk_n = sum(1 for ch, g in cmap.items() if g >= 192 and "\u4e00" <= ch <= "\u9fff")
    print(f"cmap entries {len(cmap)}  bank0 {sum(1 for g in cmap.values() if g < 192)}  bank1 {n1}  CJK-in-bank1 {cjk_n}")

    write_cmap(cmap, CMAP_PATH)
    print("wrote", CMAP_PATH)

    font16 = load_face(13)
    font12 = load_face(10)
    OUT.mkdir(parents=True, exist_ok=True)

    info16 = write_kiwi(ram, SRC_16, cmap, font16, OUT / "kiwi_16x16.bin")
    print(f"16x16 n0={info16['n0']} n1={info16['n1']} {info16['bytes']} bytes")
    info12 = write_kiwi(ram, SRC_12, cmap, font12, OUT / "kiwi_12x12.bin")
    print(f"12x12 n0={info12['n0']} n1={info12['n1']} {info12['bytes']} bytes")

    atlas((OUT / "kiwi_16x16.bin").read_bytes(), cmap, OUT / "atlas_sample.png")
    preview_line(font16, "半熟英雄塞巴斯蒂安的了不是人！", 16, 16, OUT / "preview.png")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
