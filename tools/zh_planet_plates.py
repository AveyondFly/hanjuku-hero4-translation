"""Planet field plate names and help (sun/mon/tue/wed/thu/fri)."""
from __future__ import annotations


def by_id() -> dict[str, str]:
    ARENA = ("场所", "不知从哪出现的", "强者们聚集之地")
    out: dict[str, str] = {}

    def arena(prefix: str) -> None:
        out[prefix] = ARENA[0]
        out[f"{prefix}_help#0"] = ARENA[1]
        out[f"{prefix}_help#1"] = ARENA[2]

    # --- 阿尔玛之月 ---
    out.update({
        "sun_f01": "阿尔玛之月",
        "sun_f01_help#0": "阿尔玛之月降坏的",
        "sun_f01_help#1": "新持所降临的坏",
        "sun_f02": "火之陨石落下处",
        "sun_f02_help#0": "不知名的火之陨",
        "sun_f02_help#1": "落下的场所",
        "sun_f03": "寂静的穴",
        "sun_f03_help#0": "最近才被发现的",
        "sun_f03_help#1": "迷宫的入口",
    })
    arena("sun_f04")
    # --- 浪漫 ---
    out.update({
        "mon_f01": "金之星",
        "mon_f01_help#0": "被闪耀的金",
        "mon_f01_help#1": "包围的星",
        "mon_f02": "梦之星",
        "mon_f02_help#0": "这颗星的住民是大",
        "mon_f02_help#1": "浪漫主义者的传闻",
        "mon_f03": "气之星",
        "mon_f03_help#0": "降临在星之世的小星",
        "mon_f03_help#1": "守得厚实所以有名？",
        "mon_f04": "坏之星",
        "mon_f04_help#0": "窥视着浪漫的",
        "mon_f04_help#1": "最大的星",
        "mon_f05": "坏光的淤滞",
        "mon_f05_help#0": "贯穿星中的",
        "mon_f05_help#1": "迷宫的入口",
    })
    arena("mon_f06")
    # --- 重装 ---
    out.update({
        "tue_f01": "贾多生产配置地1",
        "tue_f01_help#0": "靠机械回坏星",
        "tue_f01_help#1": "被复的置地之一",
        "tue_f02": "贾多生产配置地2",
        "tue_f02_help#0": "产生机械长部队的",
        "tue_f02_help#1": "生产之间的置地",
        "tue_f03": "贾多本据地",
        "tue_f03_help#0": "从前矗在：的连之上",
        "tue_f03_help#1": "好像是某种设施",
        "tue_f04": "捕见的夹缝",
        "tue_f04_help#0": "从捕见之中出现的",
        "tue_f04_help#1": "迷宫的入口",
    })
    arena("tue_f05")
    # --- 宝瓶 ---
    out.update({
        "wed_f01": "被留下的大地",
        "wed_f01_help#0": "从状不中幸免",
        "wed_f01_help#1": "勉强存在着",
        "wed_f02": "大树",
        "wed_f02_help#0": "靠不可思议的力量",
        "wed_f02_help#1": "天使敲打着树",
        "wed_f03": "回廊",
        "wed_f03_help#0": "在巨大形今十的状况下",
        "wed_f03_help#1": "心成回廊的地",
        "wed_f04": "大树改造星",
        "wed_f04_help#0": "不可思议之力的优",
        "wed_f04_help#1": "现出了姿",
        "wed_f05": "水中之剑",
        "wed_f05_help#0": "被归在水中的",
        "wed_f05_help#1": "这颗星的王之星",
        "wed_f06": "水中的异空间",
        "wed_f06_help#0": "通向水中的",
        "wed_f06_help#1": "迷宫的入口",
    })
    arena("wed_f07")
    # --- 榆木 ---
    out.update({
        "thu_f01": "森之优先1",
        "thu_f01_help#0": "从入谁的操之造物",
        "thu_f01_help#1": "甚至感到巨大的气息",
        "thu_f02": "瘴之优先1",
        "thu_f02_help#0": "不愉快的蜘蛛之姿",
        "thu_f02_help#1": "有被讨厌的上映",
        "thu_f03": "森之优先2",
        "thu_f03_help#0": "被归在友的下方的",
        "thu_f03_help#1": "映友之连",
        "thu_f04": "瘴之优先2",
        "thu_f04_help#0": "被连困扰的巨大蜘蛛",
        "thu_f04_help#1": "不愉快地蠕动着",
        "thu_f05": "欲移开始的连",
        "thu_f05_help#0": "被地生之映包围的",
        "thu_f05_help#1": "散发大气的巨大连",
        "thu_f06": "映以之光",
        "thu_f06_help#0": "那光复着映以",
        "thu_f06_help#1": "迷宫的入口",
    })
    arena("thu_f07")
    # --- 我思故我在 ---
    out.update({
        "fri_f01": "生产板块",
        "fri_f01_help#0": "防着侵入体的",
        "fri_f01_help#1": "机关所施的板块",
        "fri_f02": "连魔板块",
        "fri_f02_help#0": "魔着星的消板块",
        "fri_f02_help#1": "成为有效据点",
        "fri_f03": "机械况入造板块",
        "fri_f03_help#0": "产生这颗星的将",
        "fri_f03_help#1": "无人的况入矗立着",
        "fri_f04": "连魔板块",
        "fri_f04_help#0": "承受对星之消大的来击",
        "fri_f04_help#1": "动复变得不稳定",
        "fri_f05": "改造系统板块",
        "fri_f05_help#0": "改造星之系统的",
        "fri_f05_help#1": "科技的集魔体",
        "fri_f06": "生命体设施板块",
        "fri_f06_help#0": "为守护有效的设施",
        "fri_f06_help#1": "将装备在此",
        "fri_f07": "系统破裂洞",
        "fri_f07_help#0": "事在·大之熟中的",
        "fri_f07_help#1": "迷宫的入口",
    })
    arena("fri_f08")
    return out
