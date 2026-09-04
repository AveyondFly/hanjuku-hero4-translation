"""Shared helper for egg encyclopedia flavor text."""
from __future__ import annotations


def e(base: str, *lines: str) -> dict[str, str]:
    if len(lines) == 1:
        return {base: lines[0]}
    return {f"{base}#{i}": t for i, t in enumerate(lines)}
