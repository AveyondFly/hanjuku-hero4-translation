"""Auto-fill egg rank-up battle lines from names + attacks."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from zh_eg_atk import by_id as atk_by_id
from zh_eg_names import NAMES

CSV = Path("/home/ubuntu/translation/extracted/translation_catalog.csv")
KANA = re.compile(r"[ぁ-んァ-ン]")


def _egg_base(sid: str) -> str:
    parts = sid.split("#")[0].split("_")
    if len(parts) >= 3:
        return "_".join(parts[:3])
    return sid.split("#")[0]


def by_id() -> dict[str, str]:
    atk = atk_by_id()
    jp_of: dict[str, str] = {}
    with CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            jp_of[row["id"]] = row.get("jp") or ""

    atk_jp_to_zh = {jp_of[aid]: azh for aid, azh in atk.items() if jp_of.get(aid)}

    out: dict[str, str] = {}
    for sid, jp in jp_of.items():
        if not sid.startswith("eg_") or not jp:
            continue
        base = _egg_base(sid)
        nm = NAMES.get(base, "")
        if "ランクアップ" in jp and nm:
            dots = "。。。" if jp.rstrip().endswith("。。。") or jp.count("。") >= 3 else "。"
            out[sid] = f"{nm}：{nm}升阶了{dots}"
            continue
        if jp.startswith("弱・") and "教えた" in jp:
            skill_jp = jp[len("弱・") :]
            skill_jp = skill_jp.replace("力を教えた。。", "").replace("力を教えた。", "")
            skill_zh = atk_jp_to_zh.get(skill_jp)
            if skill_zh and not KANA.search(skill_zh):
                out[sid] = f"新招·{skill_zh}记住了。。"
    return {k: v for k, v in out.items() if not KANA.search(v)}
