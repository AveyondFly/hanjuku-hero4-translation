#!/usr/bin/env python3
"""Minimal ISO9660 extractor for Mode-1 2048-byte PS2 DVDs."""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

SECTOR = 2048


def read_sector(fp, n: int) -> bytes:
    fp.seek(n * SECTOR)
    data = fp.read(SECTOR)
    if len(data) != SECTOR:
        raise EOFError(f"short read at sector {n}")
    return data


def both_u32(b: bytes, off: int) -> int:
    return struct.unpack_from("<I", b, off)[0]


def both_u16(b: bytes, off: int) -> int:
    return struct.unpack_from("<H", b, off)[0]


def parse_name(raw: bytes) -> str:
    if raw in (b"\x00", b"\x01"):
        return ""
    name = raw.split(b";", 1)[0]
    return name.decode("latin1")


def iter_dir_records(blob: bytes):
    i = 0
    n = len(blob)
    while i < n:
        length = blob[i]
        if length == 0:
            # pad to next sector
            nxt = (i // SECTOR + 1) * SECTOR
            if nxt <= i:
                break
            i = nxt
            continue
        rec = blob[i : i + length]
        if len(rec) < 34:
            break
        ext_len = rec[1]
        lba = both_u32(rec, 2)
        size = both_u32(rec, 10)
        flags = rec[25]
        name_len = rec[32]
        name = parse_name(rec[33 : 33 + name_len])
        yield {
            "lba": lba,
            "size": size,
            "flags": flags,
            "name": name,
            "is_dir": bool(flags & 0x02),
        }
        i += length


def extract(iso_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with iso_path.open("rb") as fp:
        pvd = read_sector(fp, 16)
        if pvd[0] != 1 or pvd[1:6] != b"CD001":
            raise SystemExit("not an ISO9660 PVD at sector 16")
        root = pvd[156 : 156 + 34]
        root_lba = both_u32(root, 2)
        root_size = both_u32(root, 10)
        vol_id = pvd[40:72].decode("latin1").strip()
        print(f"volume: {vol_id!r}  root LBA={root_lba} size={root_size}")

        def walk(lba: int, size: int, rel: Path):
            dest = out_dir / rel
            dest.mkdir(parents=True, exist_ok=True)
            blob = b""
            nsec = (size + SECTOR - 1) // SECTOR
            fp.seek(lba * SECTOR)
            blob = fp.read(nsec * SECTOR)[:size]
            for rec in iter_dir_records(blob):
                if not rec["name"]:
                    continue
                child = rel / rec["name"]
                if rec["is_dir"]:
                    print(f"  DIR  {child.as_posix()}")
                    walk(rec["lba"], rec["size"], child)
                else:
                    outp = out_dir / child
                    outp.parent.mkdir(parents=True, exist_ok=True)
                    fp.seek(rec["lba"] * SECTOR)
                    data = fp.read(rec["size"])
                    outp.write_bytes(data)
                    print(f"  FILE {child.as_posix():40s} {rec['size']:10d}")

        walk(root_lba, root_size, Path("."))


if __name__ == "__main__":
    iso = Path(sys.argv[1])
    out = Path(sys.argv[2])
    extract(iso, out)
