#!/usr/bin/env python3
"""Parse a decompressed TIM2 picture into a PIL image (8-bit or 4-bit indexed)."""
from __future__ import annotations

import struct
from PIL import Image


def _rgba32(c: int) -> tuple[int, int, int, int]:
    r = c & 0xFF
    g = (c >> 8) & 0xFF
    b = (c >> 16) & 0xFF
    a = (c >> 24) & 0xFF
    if a == 0x80:
        a = 255
    elif 0 < a < 0x80:
        a = min(255, a * 2)
    return (r, g, b, a)


def tim2_to_image(data: bytes, picture: int = 0) -> Image.Image:
    if data[:4] != b"TIM2":
        raise ValueError("not TIM2")
    n_pic = struct.unpack_from("<H", data, 6)[0]
    if not (0 <= picture < n_pic):
        raise ValueError("picture index")
    off = 16
    for _ in range(picture):
        total = struct.unpack_from("<I", data, off)[0]
        off += total
    total, clut_size, image_size, header_size, clut_colors = struct.unpack_from(
        "<IIIHH", data, off
    )
    clut_type = data[off + 18]
    image_type = data[off + 19]
    width, height = struct.unpack_from("<HH", data, off + 20)
    img_off = off + header_size
    clut_off = img_off + image_size
    pixels = data[img_off : img_off + image_size]
    pal = []
    if clut_size and clut_colors:
        for i in range(clut_colors):
            if clut_off + 4 * (i + 1) <= len(data):
                pal.append(_rgba32(struct.unpack_from("<I", data, clut_off + 4 * i)[0]))
    if image_type in (4, 6) or (image_type == 5 and image_size >= width * height):
        # 8-bit
        img = Image.frombytes("P", (width, height), pixels[: width * height])
        if pal:
            raw = []
            for rgb in pal:
                raw.extend(rgb[:3])
            img.putpalette(raw + [0] * (768 - len(raw)))
            img = img.convert("RGBA")
            # apply alpha from palette
            px = img.load()
            src = pixels
            for y in range(height):
                for x in range(width):
                    idx = src[y * width + x]
                    if idx < len(pal):
                        px[x, y] = pal[idx]
        return img
    # 4-bit
    raw_px = bytearray(width * height)
    i = 0
    for y in range(height):
        for x in range(0, width, 2):
            b = pixels[i] if i < len(pixels) else 0
            i += 1
            raw_px[y * width + x] = b & 0xF
            if x + 1 < width:
                raw_px[y * width + x + 1] = b >> 4
    img = Image.new("RGBA", (width, height))
    px = img.load()
    if not pal:
        pal = [(i * 17, i * 17, i * 17, 255) for i in range(16)]
    for y in range(height):
        for x in range(width):
            idx = raw_px[y * width + x]
            px[x, y] = pal[idx] if idx < len(pal) else (255, 0, 255, 255)
    return img
