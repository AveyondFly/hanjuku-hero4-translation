"""Boss leftovers: 艾格妈妈 / TYPE-0 / 莫特 / 核导弹."""
from __future__ import annotations


def by_id() -> dict[str, str]:
    M = "艾格妈妈："
    T = "艾格妈妈：TYPE-0："
    C = "莫特·库蒙："
    S = "莫特·苏蒙："
    X = "核导弹："
    R = "记者："
    P = "总统："
    out: dict[str, str] = {}
    out.update(_mama(M))
    out.update(_emtp(T))
    out.update(_motk(C))
    out.update(_mots(S))
    out.update(_atom(X, R, P))
    return out


def _steal_lines(who: str) -> dict[str, str]:
    """Shared 'stole your command' narration (mama / TYPE-0)."""
    pairs = [
        ("ms2", "攻击1"),
        ("ms21", "攻击2"),
        ("ms21_kyobi", "回复"),
        ("ms22", "攻击3"),
        ("ms22_kyobi", "防御"),
        ("ms23", "攻击"),
        ("ms23_kyobi", "精神"),
        ("ms24", "突击"),
        ("ms25", "王牌"),
        ("ms26", "蛋"),
        ("ms27", "变形"),
        ("ms28", "哪个晶球"),
        ("ms2_ex", ""),
    ]
    out: dict[str, str] = {}
    for key, item in pairs:
        out[f"{who}_{key}#0"] = "盯上了你的指令。"
        stolen = f"{item}被夺走了。。" if item else "被夺走了。。"
        out[f"{who}_{key}#1"] = stolen
    return out


def _mama(M: str) -> dict[str, str]:
    out = {
        "eg_bo_mama_d1": M + "能量场展开，防御！",
        "eg_bo_mama_d2#0": M + "外壳损伤轻微！",
        "eg_bo_mama_d2#1": "内部未见损伤！",
        "eg_bo_mama_d3#0": M + "损伤率百分之25！",
        "eg_bo_mama_d3#1": "解析作业未见异常！",
        "eg_bo_mama_l#0": M + "能量低下，战斗继续不可能。",
        "eg_bo_mama_l#1": "吾之子未见损伤！",
        "eg_bo_mama_ms1#0": M + "艾格妈妈的能量护盾回复。",
        "eg_bo_mama_ms1#1": "弱冲击袭来了。。",
        "eg_bo_mama_ms3": M + "呼唤了导弹的集中炮击。。",
        "eg_bo_mama_vo11#0": M + "我可爱的儿子就要出生了",
        "eg_bo_mama_vo11#1": "若要妨碍，就排除。",
        "eg_bo_mama_vo14#0": M + "就快了。吾之子",
        "eg_bo_mama_vo14#1": "就要诞生。",
        "eg_bo_mama_vo15#0": M + "一想到吾之子",
        "eg_bo_mama_vo15#1": "便被祝福的喜悦包住。",
        "eg_bo_mama_vo22#0": M + "你们为什么要战斗？",
        "eg_bo_mama_vo22#1": "争斗生不出任何东西！",
        "eg_bo_mama_vo23#0": M + "被感情带走而挥拳！",
        "eg_bo_mama_vo23#1": "低水平的愚蠢之事！",
        "eg_bo_mama_vo25": M + "开始脑叶切除手术！",
        "eg_bo_mama_vo31#0": M + "请祝福！",
        "eg_bo_mama_vo31#1": "吾之子马上就要诞生。",
        "eg_bo_mama_vo32#0": M + "为可爱儿子的诞生",
        "eg_bo_mama_vo32#1": "举起祝贺吧。",
        "eg_bo_mama_vo33": M + "看来再谈也是徒劳。",
        "eg_bo_mama_w#0": M + "确认敌方生命活动停止！",
        "eg_bo_mama_w#1": "开始解析作业！",
    }
    stolen = _steal_lines("eg_bo_mama")
    for k, v in stolen.items():
        if k.endswith("#0"):
            stolen[k] = M + "盯上了你的指令。"
    out.update(stolen)
    return out


def _emtp(T: str) -> dict[str, str]:
    out = {
        "eg_bo_emtp_d1": T + "目标的攻击造成损伤。",
        "eg_bo_emtp_d2": T + "警报。警报。",
        "eg_bo_emtp_d3": T + "破损处检查开始！",
        "eg_bo_emtp_l#0": T + "紧急。紧急。",
        "eg_bo_emtp_l#1": "主系统宕机！",
        "eg_bo_emtp_ms1#0": T + "艾格妈妈：TYPE-0的弱冲击",
        "eg_bo_emtp_ms1#1": "袭来了。。",
        "eg_bo_emtp_ms3": T + "呼唤了导弹的集中炮击。。",
        "eg_bo_emtp_vo11#0": T + "我是艾格妈妈：TYPE-0！",
        "eg_bo_emtp_vo11#1": "为了人类的进化而被开发！",
        "eg_bo_emtp_vo13#0": T + "你们已经大幅超出",
        "eg_bo_emtp_vo13#1": "人类的平均值！",
        "eg_bo_emtp_vo14#0": T + "为了目的，将采集",
        "eg_bo_emtp_vo14#1": "你们的数据！",
        "eg_bo_emtp_vo21#0": T + "个人的私欲会妨碍",
        "eg_bo_emtp_vo21#1": "人类的进化！",
        "eg_bo_emtp_vo23": T + "要构筑人类新的历史！",
        "eg_bo_emtp_vo24#0": T + "为何害怕进化？",
        "eg_bo_emtp_vo24#1": "生命的历史就是进化的历史！",
        "eg_bo_emtp_vo31": T + "自我防护程序启动。",
        "eg_bo_emtp_vo34": T + "若不解除武装就攻击。",
        "eg_bo_emtp_vo35#0": T + "迫不得已！",
        "eg_bo_emtp_vo35#1": "强制排除。",
        "eg_bo_emtp_w#0": T + "目标消灭！",
        "eg_bo_emtp_w#1": "数据采集不可能！",
    }
    stolen = _steal_lines("eg_bo_emtp")
    for k, v in stolen.items():
        if k.endswith("#0"):
            stolen[k] = T + "盯上了你的指令。"
    out.update(stolen)
    return out


def _motk(C: str) -> dict[str, str]:
    return {
        "eg_bo_motk_d1": C + "难吃的东西最讨厌4。。",
        "eg_bo_motk_d2": C + "忌避4。。",
        "eg_bo_motk_d3": C + "呜哦欸。。",
        "eg_bo_motk_l": C + "啊呀啪。还想再吃4！",
        "eg_bo_motk_ms1#0": C + "被套上了消化。",
        "eg_bo_motk_ms1#1": "刺激强过头了。。",
        "eg_bo_motk_ms2": C + "被吃掉了。",
        "eg_bo_motk_ms21": C + "被吃掉了。",
        "eg_bo_motk_ms22": C + "没能吃掉。",
        "eg_bo_motk_ms22_a": C + "有一名将军被吃掉了。",
        "eg_bo_motk_ms23": C + "被吐出来了。",
        "eg_bo_motk_ms3": C + "莫特·库蒙把对方吃了。",
        "eg_bo_motk_ms31#0": C + "莫特·库蒙",
        "eg_bo_motk_ms31#1": "没能吃掉！",
        "eg_bo_motk_ms32#0": C + "莫特·库蒙把蟑螂布丁吃掉了。",
        "eg_bo_motk_ms32#1": "啊啊，拉肚子了！",
        "eg_bo_motk_ms33#0": C + "莫特·库蒙把卡特莉·伊奈巧克力吃掉了。",
        "eg_bo_motk_ms33#1": "啊啊，拉肚子了！",
        "eg_bo_motk_ms3_a#0": C + "莫特·库蒙把对方吃了。",
        "eg_bo_motk_vo11": C + "哇哦。好猛。看起来好好吃4。",
        "eg_bo_motk_vo12": C + "咸的甜的辣的4。",
        "eg_bo_motk_vo14": C + "嗬呀嗬呀嗬呀。起劲4。。",
        "eg_bo_motk_vo21": C + "我开动了猛犸4。。",
        "eg_bo_motk_vo24": C + "边跳边吃4。",
        "eg_bo_motk_vo25": C + "再吃点嘛——。。",
        "eg_bo_motk_vo25_a": C + "多谢款待4哟",
        "eg_bo_motk_vo25_b": C + "这是啥啊。难吃4。",
        "eg_bo_motk_vo25_c": C + "嚼起来好脆4哟",
        "eg_bo_motk_vo25_d": C + "在肚子里跳4哟",
        "eg_bo_motk_vo31": C + "呜哟。找到好吃的了4。",
        "eg_bo_motk_vo32": C + "哼哼。点心4。",
        "eg_bo_motk_vo35": C + "王牌吃嘛——。。",
        "eg_bo_motk_vo36": C + "拿来下酒正好4。",
        "eg_bo_motk_vo36_a": C + "好痛痛痛。肚皮占卜4。",
        "eg_bo_motk_vo37": C + "垃圾食品最喜欢4。",
        "eg_bo_motk_vo38": C + "停不下来的好吃4。",
        "eg_bo_motk_vo4": C + "中嘻中嘻。。",
        "eg_bo_motk_w": C + "莫特就是吃了再吃再吃个不停4。",
    }


def _mots(S: str) -> dict[str, str]:
    return {
        "eg_bo_mots_d1": S + "弱的弱的尽管来4。",
        "eg_bo_mots_d2": S + "软脚4。",
        "eg_bo_mots_d3": S + "唔唔唔！",
        "eg_bo_mots_l": S + "啪嗒倒下。该再攻才对4！",
        "eg_bo_mots_ms1#0": S + "莫特·苏蒙把披风绞上了。",
        "eg_bo_mots_ms1#1": "变得很难打出伤害！",
        "eg_bo_mots_ms12#0": S + "莫特·苏蒙正在绞披风！",
        "eg_bo_mots_ms12#1": "很难打出伤害！",
        "eg_bo_mots_ms2#0": S + "莫特·苏蒙的披风被打开了。",
        "eg_bo_mots_ms2#1": "力量被敌人吸走了。。",
        "eg_bo_mots_ms3#0": S + "攻变之一袭向了莫特·苏蒙。",
        "eg_bo_mots_ms3#1": "力量被狠狠吸走了。。",
        "eg_bo_mots_ms3_b#0": S + "攻变之一袭向了莫特·苏蒙。",
        "eg_bo_mots_ms3_b#1": "力量被吸走一半。。",
        "eg_bo_mots_vo11": S + "你们的实力什么的算什么4。",
        "eg_bo_mots_vo13": S + "凡事绞紧才够本4！",
        "eg_bo_mots_vo14": S + "呼哈哈哈哈哈哈哈哈——！",
        "eg_bo_mots_vo21": S + "来吧4。时辰到了，向自己的挑战4。。",
        "eg_bo_mots_vo24": S + "那个收下了4。拜拜。",
        "eg_bo_mots_vo25": S + "再吸点嘛——。",
        "eg_bo_mots_vo32": S + "再把容量放大4。",
        "eg_bo_mots_vo34": S + "混沌漩涡4。",
        "eg_bo_mots_vo35": S + "自由的——死——。发烧。。",
        "eg_bo_mots_vo4": S + "中嘻中嘻。。",
        "eg_bo_mots_w": S + "莫特就是攻了再攻再攻个不停4！",
    }


def _atom(X: str, R: str, P: str) -> dict[str, str]:
    return {
        "eg_bo_atom_l#0": X + "速报【总统。导弹击中的速报。",
        "eg_bo_atom_l#1": P + "什、什么。？",
        "eg_bo_atom_ms1": X + "核导弹把战场的天空划开了空间。。",
        "eg_bo_atom_ms2": X + "核导弹被导弹对射了。。",
        "eg_bo_atom_ms3#0": "当地传来哀叹核导弹发射的敌人的声音。",
        "eg_bo_atom_ms3#1": "世界在为半熟英雄们加油。。",
        "eg_bo_atom_ms3_a#0": X + "当地传来哀叹核导弹发射的敌人的声音。",
        "eg_bo_atom_ms3_a#1": "世界在为半熟英雄们加油。。",
        "eg_bo_atom_ms3_b": X + "力量涌上来了！",
        "eg_bo_atom_telop#2": "紧急新闻地球联邦紧急",
        "eg_bo_atom_vo11": X + "目标锁定。开火。",
        "eg_bo_atom_vo12": X + "哇啊——。救、救命——。。",
        "eg_bo_atom_vo13": X + "你这。军人。。",
        "eg_bo_atom_vo21": X + "打——。",
        "eg_bo_atom_vo22": X + "别靠近导弹。",
        "eg_bo_atom_vo23": X + "怪物啊。。",
        "eg_bo_atom_vo31": X + "收到收到。",
        "eg_bo_atom_vo32": "把核，把核停下来。",
        "eg_bo_atom_vo33": "一二三四五六七八。",
        "eg_bo_atom_vo34": "邦日尔，红酒劳驾。",
        "eg_bo_atom_vo35": "沃尔夫冈豹二世再见。",
        "eg_bo_atom_vo36": "玛格丽特海鲜饭真香。",
        "eg_bo_atom_vo37": "弗拉门戈斗牛士拜托。",
        "eg_bo_atom_vo38": "好哇皮罗什基套娃。",
        "eg_bo_atom_vo39": "世界和平万岁。",
        "eg_bo_atom_vo3_ed1#0": R + "曾经，世界有过如此团结",
        "eg_bo_atom_vo3_ed1#1": "的时候吗。？",
        "eg_bo_atom_vo3_ed2#0": R + "是啊，我们生命的希望",
        "eg_bo_atom_vo3_ed2#1": "托付给了英雄。",
        "eg_bo_atom_vo3_st#0": X + R + "英雄发射的导弹",
        "eg_bo_atom_vo3_st#1": "被看作战术核的看法变强了。",
        "eg_bo_atom_w#0": X + "总统们，守和平。守未来。",
        "eg_bo_atom_w#1": "不会对军人们的决意妥协。。",
    }
