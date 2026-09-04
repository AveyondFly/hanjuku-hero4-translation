#!/usr/bin/env python3
"""UDF 1.02/1.50 directory listing and extraction for PS2 DVDs."""
from __future__ import annotations

import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

SECTOR = 2048


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def u64(b, o):
    return struct.unpack_from("<Q", b, o)[0]


def tag_id(sec: bytes) -> int:
    return u16(sec, 0)


def decode_dstring(b: bytes) -> str:
    if not b:
        return ""
    if b[0] == 8:
        return b[1:].split(b"\x00", 1)[0].decode("latin1", "replace").strip()
    if b[0] == 16:
        raw = b[1:]
        if len(raw) % 2:
            raw = raw[:-1]
        return raw.decode("utf-16-be", "replace").split("\x00", 1)[0].strip()
    return b.split(b"\x00", 1)[0].decode("latin1", "replace").strip()


def decode_cs0(b: bytes) -> str:
    if not b:
        return ""
    if b[0] == 8:
        return b[1:].decode("latin1", "replace")
    if b[0] == 16:
        raw = b[1:]
        if len(raw) % 2:
            raw = raw[:-1]
        return raw.decode("utf-16-be", "replace")
    return b.decode("latin1", "replace")


@dataclass
class LongAd:
    length: int
    lba: int  # partition-relative
    part: int


def parse_long_ad(b: bytes, o: int = 0) -> LongAd:
    length = u32(b, o) & 0x3FFFFFFF
    lba = u32(b, o + 4)
    part = u16(b, o + 8)
    return LongAd(length, lba, part)


class UDF:
    def __init__(self, fp):
        self.fp = fp
        self.part_start = 0
        self.part_len = 0
        self.root_icb = None

    def read_lba(self, abs_lba: int, n=1) -> bytes:
        self.fp.seek(abs_lba * SECTOR)
        return self.fp.read(n * SECTOR)

    def read_part(self, part_lba: int, n=1) -> bytes:
        return self.read_lba(self.part_start + part_lba, n)

    def init(self):
        avdp = self.read_lba(256)
        if tag_id(avdp) != 2:
            avdp = self.read_lba(512)
            if tag_id(avdp) != 2:
                raise SystemExit(f"no AVDP (tag={tag_id(avdp)})")
        # extent_ad: length then location (bytes, LBA)
        mvds_len = u32(avdp, 16)
        mvds_lba = u32(avdp, 20)
        print(f"AVDP ok  MVDS LBA={mvds_lba} len={mvds_len}")
        nsec = max(1, (mvds_len + SECTOR - 1) // SECTOR)
        fsd_ad = None
        for i in range(nsec):
            sec = self.read_lba(mvds_lba + i)
            tid = tag_id(sec)
            if tid == 5:  # Partition Descriptor
                self.part_start = u32(sec, 188)
                self.part_len = u32(sec, 192)
                print(f"Partition start={self.part_start} len={self.part_len}")
            elif tid == 6:  # Logical Volume Descriptor
                # File Set Descriptor lives in Logical Volume Contents Use (long_ad @ 248)
                fsd_ad = parse_long_ad(sec, 248)
                print(f"LVD FSD long_ad length={fsd_ad.length} lba={fsd_ad.lba} part={fsd_ad.part}")
        if fsd_ad is None:
            raise SystemExit("no Logical Volume Descriptor / FSD")
        fsd = self.read_part(fsd_ad.lba)
        if tag_id(fsd) != 256:
            raise SystemExit(f"FSD tag {tag_id(fsd)}")
        self.root_icb = parse_long_ad(fsd, 400)
        print(f"Root ICB lba={self.root_icb.lba} len={self.root_icb.length}")

    def read_file_entry(self, part_lba: int) -> bytes:
        return self.read_part(part_lba)

    def alloc_extents(self, fe: bytes):
        """Return list of (abs_lba, length_bytes) from File Entry allocation descriptors."""
        desc_tag = tag_id(fe)
        # ICB Tag flags at byte 34 (bits 0-2 = alloc desc type)
        adtype = u16(fe, 34) & 0x07
        if desc_tag == 261:  # File Entry
            l_ea = u32(fe, 168)
            l_ad = u32(fe, 172)
            rec_len = u64(fe, 56)
            start = 176 + l_ea
        elif desc_tag == 266:  # Extended File Entry
            l_ea = u32(fe, 212)
            l_ad = u32(fe, 216)
            rec_len = u64(fe, 56)
            start = 216 + l_ea
        else:
            raise ValueError(f"not a file entry tag={desc_tag}")
        if adtype == 3:
            # data is stored immediately in the file entry
            return rec_len, []
        extents = []
        off = start
        end = start + l_ad
        # adtype 0=short_ad(8), 1=long_ad(16), 3=extended
        while off + 8 <= end and off + 8 <= len(fe):
            if adtype == 0:
                length = u32(fe, off) & 0x3FFFFFFF
                flags = u32(fe, off) >> 30
                loc = u32(fe, off + 4)
                off += 8
            elif adtype == 1:
                length = u32(fe, off) & 0x3FFFFFFF
                flags = u32(fe, off) >> 30
                loc = u32(fe, off + 4)
                off += 16
            else:
                length = u32(fe, off) & 0x3FFFFFFF
                flags = u32(fe, off) >> 30
                loc = u32(fe, off + 4)
                off += 20 if adtype == 3 else 8
            if length == 0:
                break
            if flags != 1:  # skip next-extent pointers somewhat
                extents.append((self.part_start + loc, length))
        return rec_len, extents

    def read_file_bytes(self, fe: bytes) -> bytes:
        info_len, extents = self.alloc_extents(fe)
        adtype = u16(fe, 34) & 0x07
        if adtype == 3:
            if tag_id(fe) == 261:
                l_ea = u32(fe, 168)
                l_ad = u32(fe, 172)
                start = 176 + l_ea
            else:
                l_ea = u32(fe, 212)
                l_ad = u32(fe, 216)
                start = 216 + l_ea
            return fe[start : start + info_len]
        chunks = []
        remain = info_len
        for abs_lba, length in extents:
            n = min(length, remain)
            self.fp.seek(abs_lba * SECTOR)
            chunks.append(self.fp.read(n))
            remain -= n
            if remain <= 0:
                break
        data = b"".join(chunks)
        return data[:info_len]

    def walk(self, icb_lba: int, rel: str, out_dir: Path | None, listing: list):
        fe = self.read_file_entry(icb_lba)
        # ICB Tag File Type at offset 27 (4 = directory)
        ftype = fe[27]
        data = self.read_file_bytes(fe)
        if ftype != 4:
            return
        i = 0
        while i + 38 <= len(data):
            if u16(data, i) != 257:
                # pad to next sector
                nxt = (i // SECTOR + 1) * SECTOR
                if nxt <= i:
                    break
                i = nxt
                continue
            l_fi = data[i + 19]
            l_iu = u16(data, i + 36)
            length = (38 + l_iu + l_fi + 3) & ~3
            if length < 40 or i + length > len(data) + 3:
                # last record may not overflow much
                if i + 38 + l_iu + l_fi > len(data):
                    break
                length = min(length, len(data) - i)
            fid = data[i : i + length]
            file_char = fid[18]
            icb = parse_long_ad(fid, 20)
            raw_name = fid[38 + l_iu : 38 + l_iu + l_fi]
            name = decode_cs0(raw_name).rstrip("\x00")
            i += length
            if file_char & 0x08 or file_char & 0x04:
                continue
            if not name:
                continue
            path = f"{rel}/{name}" if rel else name
            is_dir = bool(file_char & 0x02)
            child_fe = self.read_file_entry(icb.lba)
            info_len, extents = self.alloc_extents(child_fe)
            listing.append((path, is_dir, info_len, extents[:1]))
            print(f"{'DIR ' if is_dir else 'FILE'} {path:50s} {info_len:12d}")
            if is_dir:
                self.walk(icb.lba, path, out_dir, listing)
            elif out_dir is not None:
                dest = out_dir / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(self.read_file_bytes(child_fe))


def main():
    iso = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    do_extract = len(sys.argv) > 3 and sys.argv[3] == "extract"
    listing = []
    with iso.open("rb") as fp:
        u = UDF(fp)
        u.init()
        out_dir = out if do_extract else None
        if out_dir:
            out_dir.mkdir(parents=True, exist_ok=True)
        u.walk(u.root_icb.lba, "", out_dir, listing)
    list_path = (out or Path(".")) / "udf_listing.txt"
    if out:
        out.mkdir(parents=True, exist_ok=True)
        list_path = out / "udf_listing.txt"
        with list_path.open("w") as f:
            for path, is_dir, size, ext in listing:
                f.write(f"{'DIR' if is_dir else 'FILE'}\t{size}\t{path}\n")
        print("wrote", list_path, "entries", len(listing))


if __name__ == "__main__":
    main()
