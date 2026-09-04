"""Leftover sysmes phrases, font tests, inu viewer. Skip ASCII-English originals."""
from __future__ import annotations


def by_id() -> dict[str, str]:
    out: dict[str, str] = {
        # sound menu: ステレオ / モノラル / 振動
        "sysmes_sound_config_term#0": "立",
        "sysmes_sound_config_term#1": "体",
        "sysmes_sound_config_term#2": "单",
        "sysmes_sound_config_term#3": "声",
        "sysmes_sound_config_term#8": "振",
        "sysmes_sound_config_term#9": "动",
        "sysmes_sound_config_term#10": "开",
        "sysmes_term_b#18": "的坏",
        "sysmes_term_b#25": "设定",
        "sysmes_term_b#34": "ー",
        # font / mic / conversation tests (jp was kana)
        "301#0": "连。啊斗优",
        "301#1": "傻瓜败字体",
        "301#2": "傻瓜字体。",
        "32#0": "麦克风测试中",
        "32#1": "……",
        "32#2": "啊",
        "32#3": "咦",
        "inu_viewer01#0": "打强今友",
        "inu_viewer01#1": "知新新以金力1",
        "inu_viewer01#2": "知新新以金力2",
        "inu_viewer02#0": "大新以形新1",
        "inu_viewer02#1": "大新形以新2",
        "inu_viewer02#2": "知新以败所打",
    }
    # Shift-JIS-mojibake message ids; jp is Japanese test copy
    tag = "^OeXg"
    out[f"{tag}#0"] = "标题姿"
    for i in range(1, 9):
        out[f"{tag}#{i}"] = f"标题{i}姿"
    for i in range(8):
        out[f"{tag}#{i + 9}"] = f"副标题{i + 1}姿"
    conv = "ïbeXg"
    conv_zh = [
        "啊啊啊？？？",
        "咦咦咦",
        "呜呜呜……",
        "诶诶诶诶全。",
        "哦哦哦哦",
        "咔咔咔啊始金",
        "基基基得情",
        "库库库气嘿",
        "科科科啊",
        "可可可咦",
        "萨萨萨拉",
        "西西西苏",
        "苏苏苏啊",
        "塞塞塞啊",
        "索索索",
        "西奥列维形杰间列间",
        "气情2啊",
    ]
    for i, z in enumerate(conv_zh):
        out[f"{conv}#{i}"] = z
    out["ïbeXgQ"] = "啊啊啊"
    out["ïbeXgR"] = "塞巴斯蒂安选塔铃！"
    out["L#0"] = "繰部队长心配集团明攻番号○与"
    out["L#1"] = "将殿可挑使空箱：造繰移动周捕"
    out["L#2"] = "」任中敌「」合「"
    sel = "IðeXg"
    out[f"{sel}#0"] = "啊"
    out[f"{sel}#1"] = "咦"
    out[f"{sel}#2"] = "呜诶"
    out[f"{sel}#3"] = "哦哦哦"
    out["²¯eXg"] = "窗口要漏出去了。"
    return out
