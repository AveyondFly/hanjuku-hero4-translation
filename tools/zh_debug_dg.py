"""Dungeon debug menus (绘美铃 / 迷宫旗标)."""
from __future__ import annotations


def _flags(prefix: str, stem: str, nums: list) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, n in enumerate(nums):
        out[f"{prefix}#{i}"] = f"{stem}{n:03d}" if n >= 100 or stem.endswith("0") else f"{stem}{n:02d}"
    return out


def by_id() -> dict[str, str]:
    E = "绘美铃："
    out: dict[str, str] = {
        "dg_debug#0": "助手我在给下田君当助手",
        "dg_debug#1": "叫绘美！",
        "dg_debug#2": "请叫我绘美铃。",
        "dg_debug#3": "绘美铃呐，你想把哪个旗标",
        "dg_debug#4": "打开？",
        "dg_debug2#0": "勇的笑话",
        "dg_debug2#1": "勇的机关",
        "dg_debug2#2": "日",
        "dg_debug2#3": "月·火",
        "dg_debug2#4": "水",
        "dg_debug2#5": "木·金",
        "dg_debug2#6": "主线",
        "dg_debug2#7": "确认旗标",
        "dg_debug2#8": "想要小钥匙",
        "dg_debug2#9": "已经没有了",
        "dg_debug3#0": E + "已经把迷宫旗标",
        "dg_debug3#1": "已经排好了！",
        "dg_debug3#2": "对别人是秘密……所以哦！",
        "dg_debug4#0": E + "哼！",
        "dg_debug4#1": "要是没什么用处的话",
        "dg_debug4#2": "我可要回去了！",
        "dg_debug5": E + "还有别的要事吗？",
        "dg_debug_key#0": E + "真没办法！",
        "dg_debug_key#1": "已经放进你的宝物袋",
        "dg_debug_key#2": "里四把了！",
    }
    for i in range(10):
        out[f"dg_debug2_2#{i}"] = f"开{i + 1}号" if i < 9 else "最终号"
    # 迷宫旗标 NNN (始道複眠気気複眠気気)
    groups = {
        "dg_debug2_01": [1, 2, 3, 4, 5],
        "dg_debug2_02": [101, 102, 103, 104],
        "dg_debug2_03": [201, 202, 203],
        "dg_debug2_04": [301, 302, 303, 304],
        "dg_debug2_05": [401, 402, 403, 404],
        "dg_debug2_06": [501, 502, 503],
        "dg_debug2_07": [601, 602, 603, 604, 605, 606],
        "dg_debug2_08": [701, 702, 716, 717, 718, 719, 720],
        "dg_debug2_09": [801, 802, 803],
        "dg_debug2_10": [901, 902, 903, 904, 905, 906, 907, 908, 909, 910],
    }
    for pref, nums in groups.items():
        for i, n in enumerate(nums):
            out[f"{pref}#{i}"] = f"迷宫旗标{n:03d}"
    for i in range(9):
        out[f"dg_debug2_egg#{i}"] = f"迷宫旗标蛋{i + 1:02d}"
    for i in range(11):
        out[f"dg_debug2_ice#{i}"] = f"迷宫旗标冰{i + 1:02d}"
    out["dg_debug2_ice#11"] = "迷宫旗标铁拳全"
    out["dg_debug2_mon#0"] = "迷宫旗标浪漫001"
    out["dg_debug2_mon#1"] = "迷宫旗标浪漫梦001"
    for i in range(10):
        out[f"dg_debug2_sun#{i}"] = f"迷宫旗标阿尔玛{(i + 1):03d}"
    for i in range(9):
        out[f"dg_debug2_tekken#{i}"] = f"迷宫旗标铁拳{i + 1:02d}"
    out["dg_debug2_thu#0"] = "迷宫旗标榆木001"
    out["dg_debug2_thu#1"] = "迷宫旗标榆木002"
    out["dg_debug2_thu#2"] = "迷宫旗标榆木003"
    out["dg_debug2_thu#3"] = "迷宫旗标铁拳打001"
    for i in range(11):
        out[f"dg_debug2_wed#{i}"] = f"迷宫旗标宝瓶{(i + 1):03d}"
    return out
