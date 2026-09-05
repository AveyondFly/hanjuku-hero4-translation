#!/usr/bin/env python3
"""LZSS used by Hanjuku Hero 4 (SLPM-65839) file wrapper.

Layout (matches EE 0x22bc28):
  u32 packed_size   # end = src + packed_size
  u32 unpacked_size
  LZSS payload

Flag byte, LSB first: 1 = literal, 0 = 2-byte match
  match: offset = b0 | ((b1 & 0xF0) << 4)   # 12-bit
         length = (b1 & 0x0F) + 3
  ring size 4096, start 0xFEE; bytes before dest_base are written as 0.
"""
from __future__ import annotations

import struct


def lzss_decompress(src: bytes) -> bytes:
    if len(src) < 8:
        return b""
    packed_size, unpacked_size = struct.unpack_from("<II", src, 0)
    end = min(packed_size, len(src))
    i = 8
    out = bytearray()
    flags = 0
    nbits = 0
    while i < end:
        if nbits == 0:
            flags = src[i]
            i += 1
            nbits = 8
            if i >= end:
                break
        if flags & 1:
            out.append(src[i])
            i += 1
        else:
            if i + 1 >= end:
                break
            b0 = src[i]
            b1 = src[i + 1]
            i += 2
            offset = b0 | ((b1 & 0xF0) << 4)
            length = (b1 & 0x0F) + 3
            dst = len(out)
            v1 = (dst + 0xFEE - offset) & 0xFFF
            src_pos = dst - v1
            for _ in range(length):
                if src_pos < 0:
                    out.append(0)
                else:
                    out.append(out[src_pos])
                src_pos += 1
        flags >>= 1
        nbits -= 1
        if unpacked_size and len(out) >= unpacked_size:
            break
    if unpacked_size and len(out) > unpacked_size:
        return bytes(out[:unpacked_size])
    return bytes(out)


def maybe_decompress(data: bytes) -> bytes:
    """Decompress if it looks like the 8-byte LZSS wrapper; else return as-is."""
    if len(data) < 16:
        return data
    packed, unpacked = struct.unpack_from("<II", data, 0)
    if packed == len(data) and 8 < unpacked < 16 * 1024 * 1024 and unpacked >= packed:
        return lzss_decompress(data)
    return data


def lzss_compress(raw: bytes) -> bytes:
    """Compress to the 8-byte header + flag/literal/match stream.

    Greedy 3-byte hash; window 4096, match length 3–18. Not bit-identical
    to the original encoder, but decompresses with lzss_decompress.
    """
    n = len(raw)
    out = bytearray()
    i = 0
    last: dict[int, list[int]] = {}

    def key3(p: int) -> int:
        return raw[p] | (raw[p + 1] << 8) | (raw[p + 2] << 16)

    def emit_group(items: list[tuple]) -> None:
        flags = 0
        payload = bytearray()
        for bit, item in enumerate(items):
            if item[0] == "L":
                flags |= 1 << bit
                payload.append(item[1])
            else:
                length, offset = item[1], item[2]
                payload.append(offset & 0xFF)
                payload.append(((offset >> 4) & 0xF0) | ((length - 3) & 0x0F))
        out.append(flags)
        out.extend(payload)

    group: list[tuple] = []
    while i < n:
        best_len = 1
        best_off = 0
        if i + 2 < n:
            k = key3(i)
            hist = last.get(k, [])
            dst = i
            for src_pos in reversed(hist):
                if dst - src_pos > 4095:
                    break
                max_l = min(18, n - i)
                l = 0
                while l < max_l and raw[src_pos + l] == raw[i + l]:
                    l += 1
                if l > best_len:
                    best_len = l
                    best_off = (src_pos + 0xFEE) & 0xFFF
                    if best_len == 18:
                        break
            if k not in last:
                last[k] = []
            last[k].append(i)
            if len(last[k]) > 64:
                last[k] = last[k][-32:]
        if best_len >= 3:
            group.append(("M", best_len, best_off))
            # index skipped 3-byte keys so later searches still work
            for p in range(i + 1, min(i + best_len, n - 2)):
                k = key3(p)
                if k not in last:
                    last[k] = []
                last[k].append(p)
            i += best_len
        else:
            group.append(("L", raw[i]))
            i += 1
        if len(group) == 8:
            emit_group(group)
            group = []
    if group:
        emit_group(group)
    payload = bytes(out)
    packed = 8 + len(payload)
    return struct.pack("<II", packed, n) + payload
