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
