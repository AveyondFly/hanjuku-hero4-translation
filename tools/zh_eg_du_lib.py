"""Dungeon-egg battle lines helper."""
from __future__ import annotations


def D(*pairs: tuple[str, str]) -> dict[str, str]:
    return {k: v for k, v in pairs}
