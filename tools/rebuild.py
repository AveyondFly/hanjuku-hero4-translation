#!/usr/bin/env python3
"""One-shot: normalize catalog, rebuild font if zh needs new glyphs, patch ISO.

Default path:

  apply_zh.py
    → build_kiwi_font.py   (only if cmap is missing characters, or --force-font)
    → patch_iso.py         (decoder + font pack + recode mes)
    → patch_generals.py

Refuses to write the ISO while PCSX2 is running (override: --allow-pcsx2).
Does not kill the emulator. --check reports missing glyphs and exits.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zh_csv import CMAP_CSV, missing_cmap_chars  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
PCSX2_NAMES = ("pcsx2-qt", "pcsx2", "PCSX2")


def run_tool(name: str, extra: list[str] | None = None) -> None:
    cmd = [sys.executable, str(TOOLS / name), *(extra or [])]
    print(f"\n==> {name}" + (f" {' '.join(extra)}" if extra else ""))
    subprocess.check_call(cmd, cwd=ROOT)


def pcsx2_pids() -> list[str]:
    found: list[str] = []
    for name in PCSX2_NAMES:
        r = subprocess.run(
            ["pgrep", "-x", name],
            capture_output=True,
            text=True,
            check=False,
        )
        found.extend(p for p in r.stdout.split() if p)
    return sorted(set(found))


def report_missing(missing: dict[str, list[str]]) -> None:
    if not missing:
        print("cmap covers all catalog zh (spaces are not glyphs)")
        return
    print(f"cmap missing {len(missing)} characters:")
    for ch, ids in list(missing.items())[:40]:
        print(f"  {ch!r} U+{ord(ch):04X}  e.g. {', '.join(ids)}")
    extra = len(missing) - 40
    if extra > 0:
        print(f"  … {extra} more")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="only scan cmap vs catalog; do not write files or ISO",
    )
    ap.add_argument(
        "--skip-apply",
        action="store_true",
        help="do not run apply_zh.py",
    )
    ap.add_argument(
        "--force-font",
        action="store_true",
        help="rebuild KIWI even if cmap already covers zh",
    )
    ap.add_argument(
        "--no-iso",
        action="store_true",
        help="stop after catalog/font; do not write the ISO",
    )
    ap.add_argument(
        "--no-generals",
        action="store_true",
        help="skip patch_generals.py",
    )
    ap.add_argument(
        "--allow-pcsx2",
        action="store_true",
        help="write ISO even if PCSX2 is running (unsafe)",
    )
    args = ap.parse_args()

    if args.check:
        if not CMAP_CSV.exists():
            print("no zh_cmap.csv yet — run without --check to build it")
            return 1
        missing = missing_cmap_chars()
        report_missing(missing)
        return 1 if missing else 0

    if not args.skip_apply:
        run_tool("apply_zh.py")

    if not CMAP_CSV.exists():
        print("no zh_cmap.csv — will build font")
        need_font = True
    else:
        missing = missing_cmap_chars()
        report_missing(missing)
        need_font = args.force_font or bool(missing)

    if need_font:
        ram = ROOT / "extracted/ram/eeMemory.bin"
        if not ram.is_file():
            raise SystemExit(f"need {ram} to rasterize KIWI bank0")
        run_tool("build_kiwi_font.py")
        missing = missing_cmap_chars()
        if missing:
            report_missing(missing)
            raise SystemExit("font rebuild still missing glyphs")
        print("cmap ok after font rebuild")
    else:
        print("skip font rebuild (no new glyphs)")

    if args.no_iso:
        print("skip ISO (--no-iso)")
        return 0

    pids = pcsx2_pids()
    if pids and not args.allow_pcsx2:
        raise SystemExit(
            "PCSX2 is running (pid "
            + ", ".join(pids)
            + "). Quit it fully, then re-run. "
            "Override with --allow-pcsx2 if you really mean to write the ISO live."
        )
    if pids:
        print("WARNING: PCSX2 running; writing ISO anyway (--allow-pcsx2)")

    run_tool("patch_iso.py")
    if not args.no_generals:
        run_tool("patch_generals.py")
    print("\nrebuild done. Fully quit PCSX2 and boot the ISO; do not load old savestates.")
    print("HUD weekday-hero / kingdom names are recoded in VFS slot 0 (PrintMes stays unhooked).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e
