---
name: read-zh-catalog
description: >-
  Query and edit Hanjuku Hero 4 Chinese translations in extracted/catalog/
  (chapter sheets ch01_sun–ch08_ear, generals, dic, egg, dungeon, UI).
  Use when looking up or changing jp/zh, mes ids (ev_/sysmes_/menu_/f_sun_/gen_),
  第一章–第八章, 分表, GLOSSARY, zh_cmap, 汉化, 译文, or in-game dialogue.
---

# Read the zh catalog

Source of truth is `extracted/catalog/*.csv` (`id,jp,zh,notes,kind`). There is
no combined `translation_catalog.csv`. Sheet list and counts:
`extracted/catalog/INDEX.txt` (small — Read that).

**Never Grep or StrReplace `extracted/catalog/`.** Never Grep the repo root for
Japanese/Chinese. That scans every sheet and blows the context.

Default lookup: `python3 tools/catalog_query.py` (limit 40, cap 200).

## Which sheet

| Sheet | Belonging |
|---|---|
| `ch01_sun.csv` | 第一章 阿尔玛之月（`ev_sun` / `f_sun` / `d_sun`） |
| `ch02_mon.csv` | 第二章 浪漫 |
| `ch03_tue.csv` | 第三章 重装 |
| `ch04_wed.csv` | 第四章 宝瓶 |
| `ch05_thu.csv` | 第五章 榆木 |
| `ch06_fri.csv` | 第六章 我思故我在 |
| `ch07_gho.csv` | 第七章 幽灵／鲸／奥拉利乌姆 |
| `ch08_ear.csv` | 第八章 地球 |
| `event_solo.csv` | 个人事件 `ev_solo` |
| `event_calendar.csv` | 月次 `ev_january`… |
| `event_other.csv` | 开场／竞技场／结束等 |
| `ui_sys.csv` / `ui_menu.csv` | 系统、菜单 |
| `dic.csv` | 图鉴 `menu_dic` |
| `egg_*.csv` | 蛋怪对白 |
| `dungeon.csv` / `dungeon_other.csv` | 迷宫 |
| `battle.csv` | 王牌／头目／杂兵 |
| `generals.csv` | 将军名 `gen_zeus`，兴趣 `gen_zeus#hobby` |
| `instance.csv` | 槽 0 英雄／行星名 `inst_hero_seva` / `inst_planet_sun` |

`catalog_query.py search --sheet ch01_sun` accepts stem or filename.

## Commands

```bash
python3 tools/catalog_query.py stats
python3 tools/catalog_query.py get ev_sun_st65#0 gen_zeus inst_hero_seva inst_planet_sun
python3 tools/catalog_query.py prefix ev_sun
python3 tools/catalog_query.py search --sheet ch01_sun --zh 维纳斯
python3 tools/catalog_query.py search --jp ガクガク
python3 tools/catalog_query.py search --id sysmes_input_name --limit 20
python3 tools/catalog_query.py keys --match sun --limit 40
python3 tools/catalog_query.py glyph 抖颤我去
python3 tools/catalog_query.py set gen_no10 --zh '舒托拉斯曼'
```

One- or two-line edits: `set`, not StrReplace. After `set`, `python3 tools/apply_zh.py` if keep/alphabet must stay in sync. Bulk: `from zh_csv import load_rows, save_rows`.

## When Read is OK

- `INDEX.txt`, `GLOSSARY.txt`, `RESOURCE_MAP.txt`
- `instance.csv` (small)
- One chapter sheet (`ch01_sun.csv` … `ch08_ear.csv`) for a contiguous scene

Do **not** Read: `dic.csv`, `dungeon.csv`, `dungeon_other.csv`, `egg_*.csv`,
`event_solo.csv`, `event_other.csv`, `generals.csv`, `battle.csv`. Query those.

## Other files that also break Read

| Thing | What to do |
|---|---|
| `*.iso` (~1.8GB) | `tools/patch_iso.py` helpers; never Read |
| `extracted/ram/eeMemory.bin` | Python slice by offset |
| PCSX2 PNG snaps | shrink to `extracted/ram/*.jpg`, then Read the jpg |
| KIWI atlas PNG / `kiwi_*.bin` | font tools |
| `extracted/SLPM_658.39` | `read_bytes()` slices |

## Translation rules

- Japanese kanji must not be reused as Chinese. Names follow `extracted/GLOSSARY.txt`.
- `kind=keep` (kana tables / 合言葉): zh must equal jp. Empty jp stays empty zh.
- Generals: `kind=name` / `kind=hobby`.
- After catalog zh edits, default to `python3 tools/rebuild.py` (apply + missing-glyph font rebuild + patch ISO + generals). `rebuild.py --check` only reports cmap gaps.
- `rebuild.py` / `patch_iso.py` quit PCSX2 before writing the ISO. Do not load old savestates after a patch.
