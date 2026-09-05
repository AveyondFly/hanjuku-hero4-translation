"""Load / save the jp+zh CSVs.

Mes strings and general-card names live in extracted/catalog/*.csv
(id, jp, zh, notes, kind), split by chapter and belonging.
The font mapping is a different schema, so it stays in extracted/zh_cmap.csv.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACTED = ROOT / "extracted"
CATALOG_DIR = EXTRACTED / "catalog"
CATALOG = EXTRACTED / "translation_catalog.csv"  # legacy monolith; read-only fallback
CMAP_CSV = EXTRACTED / "zh_cmap.csv"
KEEP_CSV = EXTRACTED / "zh_keep.csv"
ALPHABET_CSV = EXTRACTED / "zh_alphabet.csv"
GENERALS_WIDE = EXTRACTED / "general_names.csv"

FIELDNAMES = ["id", "jp", "zh", "notes", "kind"]

SHEETS: list[tuple[str, str]] = [
    ("ch01_sun.csv", "第一章 阿尔玛之月（日曜）"),
    ("ch02_mon.csv", "第二章 浪漫（月曜）"),
    ("ch03_tue.csv", "第三章 重装（火曜）"),
    ("ch04_wed.csv", "第四章 宝瓶（水曜）"),
    ("ch05_thu.csv", "第五章 榆木（木曜）"),
    ("ch06_fri.csv", "第六章 我思故我在（金曜）"),
    ("ch07_gho.csv", "第七章 幽灵／鲸／奥拉利乌姆"),
    ("ch08_ear.csv", "第八章 地球"),
    ("event_solo.csv", "个人事件"),
    ("event_calendar.csv", "月次／日历事件"),
    ("event_other.csv", "开场、竞技场、通话、结束等"),
    ("ui_sys.csv", "系统文案 sysmes／存储卡"),
    ("ui_menu.csv", "菜单"),
    ("dic.csv", "图鉴"),
    ("egg_du.csv", "蛋怪对白 eg_du"),
    ("egg_bo.csv", "蛋怪对白 eg_bo"),
    ("egg_we.csv", "蛋怪对白 eg_we"),
    ("egg_pk.csv", "蛋怪对白 eg_pk"),
    ("egg_ev.csv", "蛋怪对白 eg_ev"),
    ("egg_cl.csv", "蛋怪对白 eg_cl"),
    ("egg_pw.csv", "蛋怪对白 eg_pw"),
    ("egg_ms.csv", "蛋怪对白 eg_ms"),
    ("egg_cv.csv", "蛋怪对白 eg_cv"),
    ("egg_le.csv", "蛋怪对白 eg_le"),
    ("egg_other.csv", "蛋怪对白 其余"),
    ("dungeon.csv", "迷宫主文案 d_dung"),
    ("dungeon_other.csv", "迷宫系统／教程／蛋迷宫"),
    ("battle.csv", "战斗：王牌／头目／奥之手／杂兵"),
    ("generals.csv", "将军卡片名／兴趣"),
    ("debug.csv", "调试／测试"),
    ("other.csv", "未归类"),
]
SHEET_NAMES = tuple(name for name, _ in SHEETS)
SHEET_TITLE = dict(SHEETS)

CHAPTER_TOKEN_TO_SHEET = {
    "sun": "ch01_sun.csv",
    "mon": "ch02_mon.csv",
    "tue": "ch03_tue.csv",
    "wed": "ch04_wed.csv",
    "thu": "ch05_thu.csv",
    "fri": "ch06_fri.csv",
    "gho": "ch07_gho.csv",
    "ear": "ch08_ear.csv",
}
CHAPTER_TOKENS = ("sun", "mon", "tue", "wed", "thu", "fri", "gho", "ear")

PLANET_TO_SHEET = {
    "00": "ch01_sun.csv",
    "01": "ch02_mon.csv",
    "02": "ch03_tue.csv",
    "03": "ch04_wed.csv",
    "04": "ch05_thu.csv",
    "05": "ch06_fri.csv",
    "06": "dungeon_other.csv",
    "07": "ch07_gho.csv",
    "08": "ch08_ear.csv",
}

EGG_NAMED = frozenset(
    {"du", "bo", "we", "pk", "ev", "cl", "pw", "ms", "cv", "le"}
)
MONTHS = (
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
)

# Must stay original glyph ids (kana input / 合言葉). patch_iso transcodes only.
KEEP_PREFIXES = (
    "sysmes_hiragana",
    "sysmes_katakana",
    "sysmes_dic_index_keyword",
    "menu_secret_egg_word",
)

# Name-entry grid: jp is kanji sharing those slots, zh is A–Z / digits.
ALPHABET_PREFIXES = ("sysmes_alphabet",)

# 1–2 glyph UI marks copied from jp; re-encoded through the Chinese cmap.
COPY_PREFIXES = (
    "sysmes_hyphen",
    "sysmes_question",
    "sysmes_battle_status",
    "sysmes_battle_status_enemy",
    "sysmes_egg_type_mark",
    "sysmes_egg_type_mark_broken",
    "sysmes_field_base_mark",
    "sysmes_formation_mark",
    "sysmes_term_b",
    "sysmes_term_k",
)


def id_matches(sid: str, prefixes: tuple[str, ...]) -> bool:
    for pfx in prefixes:
        if sid == pfx or sid.startswith(pfx + "#"):
            return True
    return False


def classify(sid: str, jp: str) -> str:
    if sid.startswith("gen_"):
        if not (jp or "").strip():
            return "empty"
        return "hobby" if "#hobby" in sid else "name"
    if id_matches(sid, ALPHABET_PREFIXES):
        return "alphabet"
    if id_matches(sid, KEEP_PREFIXES):
        return "keep"
    if not (jp or "").strip():
        return "empty"
    if id_matches(sid, COPY_PREFIXES):
        return "copy"
    return "text"


def _part_chapter(part: str) -> str | None:
    for tok in CHAPTER_TOKENS:
        if part == tok:
            return tok
        if (
            part.startswith(tok)
            and len(part) > len(tok)
            and part[len(tok)].isdigit()
        ):
            return tok
    return None


def _chapter_sheet(key: str) -> str | None:
    for part in key.split("_"):
        tok = _part_chapter(part)
        if tok:
            return CHAPTER_TOKEN_TO_SHEET[tok]
    return None


def _is_calendar(key: str) -> bool:
    if not key.startswith("ev_"):
        return False
    rest = key[3:]
    for month in MONTHS:
        if rest == month:
            return True
        if rest.startswith(month) and len(rest) > len(month):
            nxt = rest[len(month)]
            if nxt.isdigit() or nxt.isalpha():
                return True
    return False


def sheet_for_id(sid: str) -> str:
    """Return the catalog filename for this id."""
    key = sid.split("#", 1)[0]
    if key.startswith("gen_"):
        return "generals.csv"
    if key.startswith(("sysmes_", "memcard_", "pad_", "metamor_")):
        return "ui_sys.csv"
    if key.startswith("menu_dic"):
        return "dic.csv"
    if key.startswith("eg_"):
        bits = key.split("_")
        kind = bits[1] if len(bits) > 1 else ""
        if kind in EGG_NAMED:
            return f"egg_{kind}.csv"
        return "egg_other.csv"
    if key.startswith("d_dung"):
        return "dungeon.csv"
    if key.startswith(
        ("dg_", "d_egg", "d_trump", "ch6_", "d_gen", "d_delimoney", "d_fallin", "d_m_momo")
    ):
        return "dungeon_other.csv"
    if key.startswith("ev_solo"):
        return "event_solo.csv"
    if _is_calendar(key):
        return "event_calendar.csv"
    if (
        not key
        or not key.isascii()
        or key[0].isdigit()
        or key.startswith(("test_", "field_debug", "world_debug", "alpha_"))
    ):
        return "debug.csv"
    ch = _chapter_sheet(key)
    if ch:
        return ch
    if key.startswith("planet_"):
        num = key[7:].split("_", 1)[0]
        return PLANET_TO_SHEET.get(num, "other.csv")
    if key.startswith(("menu_", "menumes_", "fmenu_", "bmenu_", "catori_")):
        return "ui_menu.csv"
    if key.startswith(("ev_", "gameover_")):
        return "event_other.csv"
    if key.startswith(("trump_", "inu_", "boss_", "basis_", "okunote_", "general_")):
        return "battle.csv"
    return "other.csv"


def _norm_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "id": row.get("id") or "",
        "jp": row.get("jp") or "",
        "zh": row.get("zh") or "",
        "notes": row.get("notes") or "",
        "kind": row.get("kind") or "",
    }


def _load_one(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rec = _norm_row(row)
            if rec["id"]:
                rows.append(rec)
    return rows


def catalog_using_dir() -> bool:
    return CATALOG_DIR.is_dir() and any(
        (CATALOG_DIR / name).exists() for name in SHEET_NAMES
    )


def load_rows(path: Path | None = None) -> list[dict[str, str]]:
    if path is not None:
        if not path.exists():
            return []
        return _load_one(path)
    rows: list[dict[str, str]] = []
    if catalog_using_dir():
        for name in SHEET_NAMES:
            p = CATALOG_DIR / name
            if p.exists():
                rows.extend(_load_one(p))
        return rows
    if CATALOG.exists():
        return _load_one(CATALOG)
    return []


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) or "" for k in FIELDNAMES})


def _write_index(counts: dict[str, int]) -> None:
    lines = [
        "半熟英雄4 译文分表",
        "================",
        "",
        "目录：extracted/catalog/",
        "列：id, jp, zh, notes, kind",
        "查询：python3 tools/catalog_query.py get|prefix|search|set|stats",
        "灌盘读整个目录；改某一章只改对应 csv。",
        "将军名 id 为 gen_zeus，兴趣为 gen_zeus#hobby。",
        "",
        "文件\t行数\t说明",
    ]
    total = 0
    for name, title in SHEETS:
        n = counts.get(name, 0)
        total += n
        lines.append(f"{name}\t{n}\t{title}")
    lines.append(f"合计\t{total}")
    lines.append("")
    (CATALOG_DIR / "INDEX.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_catalog(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen: set[str] = set()
    dups = 0
    for row in rows:
        rec = _norm_row(row)
        sid = rec["id"]
        if not sid:
            continue
        if sid in seen:
            dups += 1
            continue
        seen.add(sid)
        grouped[sheet_for_id(sid)].append(rec)
    if dups:
        print(f"warning: dropped {dups} duplicate catalog ids", file=sys.stderr)
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for name in SHEET_NAMES:
        chunk = grouped.get(name, [])
        counts[name] = len(chunk)
        _write_csv(CATALOG_DIR / name, chunk)
    extra = sorted(set(grouped) - set(SHEET_NAMES))
    if extra:
        print(f"warning: unknown sheets {extra}", file=sys.stderr)
    _write_index(counts)


def save_rows(rows: list[dict[str, str]], path: Path | None = None) -> None:
    if path is None:
        save_catalog(rows)
        return
    _write_csv(path, rows)


def preserve_extra_rows(
    old: list[dict[str, str]], new: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Keep rows (e.g. generals) that a mes re-extract would otherwise drop."""
    seen = {r["id"] for r in new}
    extra = [r for r in old if r["id"] not in seen]
    return new + extra


def generals_from_wide(path: Path | None = None) -> list[dict[str, str]]:
    src = path or GENERALS_WIDE
    if not src.exists():
        return []
    out: list[dict[str, str]] = []
    with src.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            gid = (row.get("id") or "").strip()
            if not gid:
                continue
            jp_n = row.get("jp_name") or ""
            zh_n = row.get("zh_name") or ""
            notes = row.get("notes") or ""
            out.append(
                {
                    "id": gid,
                    "jp": jp_n,
                    "zh": zh_n,
                    "notes": notes,
                    "kind": classify(gid, jp_n),
                }
            )
            jp_h = row.get("jp_hobby") or ""
            zh_h = row.get("zh_hobby") or ""
            if jp_h or zh_h:
                hid = f"{gid}#hobby"
                out.append(
                    {
                        "id": hid,
                        "jp": jp_h,
                        "zh": zh_h,
                        "notes": "",
                        "kind": classify(hid, jp_h),
                    }
                )
    return out


def catalog_bytes() -> int:
    if catalog_using_dir():
        return sum(
            (CATALOG_DIR / name).stat().st_size
            for name in SHEET_NAMES
            if (CATALOG_DIR / name).exists()
        )
    if CATALOG.exists():
        return CATALOG.stat().st_size
    return 0


def catalog_source() -> Path:
    if catalog_using_dir():
        return CATALOG_DIR
    return CATALOG


def zh_by_id(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    if rows is None:
        rows = load_rows()
    return {r["id"]: r.get("zh") or "" for r in rows}


def kinds_by_id(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    if rows is None:
        rows = load_rows()
    return {r["id"]: r.get("kind") or classify(r["id"], r.get("jp") or "") for r in rows}


def load_cmap(path: Path = CMAP_CSV) -> dict[str, int]:
    out: dict[str, int] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ch = row.get("char") or ""
            if ch:
                out[ch] = int(row["glyph"])
    return out


def keep_raw(sid: str, kind: str = "") -> bool:
    if kind == "keep":
        return True
    return id_matches(sid, KEEP_PREFIXES)
