"""Shared helpers for unit encyclopedia personality packs."""
from __future__ import annotations

MOT = "参加动机："
SKL = "擅长："
HOB = "兴趣特技："


def u(
    n: int,
    m0: str,
    m1: str | None,
    s0: str,
    s1: str | None,
    h0: str,
    h1: str | None = None,
) -> dict[str, str]:
    p = f"menu_dic_{n}"
    d: dict[str, str] = {
        f"{p}#0": MOT + m0,
        f"{p}#3": SKL + s0,
        f"{p}#6": HOB + h0,
    }
    if m1 is not None:
        d[f"{p}#1"] = m1
    if s1 is not None:
        d[f"{p}#4"] = s1
    if h1 is not None:
        d[f"{p}#7"] = h1
    return d
