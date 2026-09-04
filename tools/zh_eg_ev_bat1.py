"""Evil-egg battle lines A (beal–eegg)."""
from __future__ import annotations


def by_id() -> dict[str, str]:
    B = "巴尔："
    J = "运动服恶魔："
    D = "被阵的死神："
    R = "兔子撒旦："
    S = "烟鬼风："
    W = "恶魔女："
    L = "卢丘费尔："
    G = "盖拉斯："
    E = "邪恶艾格曼："
    out: dict[str, str] = {}
    out.update(_beal(B))
    out.update(_jjdv(J))
    out.update(_nodt(D))
    out.update(_rabi(R))
    out.update(_smok(S))
    out.update(_dvwm(W))
    out.update(_lucu(L))
    out.update(_gera(G))
    out.update(_eegg(E))
    return out


def _beal(B: str) -> dict[str, str]:
    return {
        "eg_ev_beal_d": B + "巴尔对星消很协足！",
        "eg_ev_beal_l": B + "让「从口中变成谁喜吧！",
        "eg_ev_beal_ms1": B + "巴尔放出了毒雾。",
        "eg_ev_beal_ms12#0": B + "变成了亲的激。",
        "eg_ev_beal_ms12#1": "好像把毒雾吸进去了。",
        "eg_ev_beal_ms13#0": B + "变成了亲的激。",
        "eg_ev_beal_ms13#1": "好像把毒雾吸进去了。",
        "eg_ev_beal_ms2#0": B + "蜘蛛的箱、青蛙的箱）、火的分",
        "eg_ev_beal_ms2#1": "起了化学变化。",
        "eg_ev_beal_ms3#0": B + "巴尔把对方当祭品，",
        "eg_ev_beal_ms31#0": B + "巴尔把对方当祭品，",
        "eg_ev_beal_ms31#1": "全部威力上升了。。",
        "eg_ev_beal_ms32": B + "巴尔把巴尔自己当祭品了。。",
        "eg_ev_beal_ms33": B + "谁也没能献给巴尔当祭品！",
        "eg_ev_beal_ms33_b": B + "没能被献成祭品！",
        "eg_ev_beal_ms33_c": B + "没能被献成祭品！",
        "eg_ev_beal_sel3": B + "把谁献给当祭品？",
        "eg_ev_beal_vo1#0": B + "身为谁喜的吾之攻击",
        "eg_ev_beal_vo1#1": "连活过来都觉得熟属吧！",
        "eg_ev_beal_vo2#0": B + "沙————。。。咯呃呃。。。",
        "eg_ev_beal_vo2#1": "嗯喵————————。。。",
        "eg_ev_beal_vo3#0": B + "想要力量吗？若要再周力",
        "eg_ev_beal_vo3#1": "就把祭品献上吧。。",
        "eg_ev_beal_vo31#0": B + "也好。依疲用",
        "eg_ev_beal_vo31#1": "把被封印的占之力解开吧。。",
        "eg_ev_beal_vo32": B + "嗯？是吾自己吗？唔啵哦啊啊。。。",
        "eg_ev_beal_vo33#0": B + "没种的家伙。",
        "eg_ev_beal_vo33#1": "被这核包住就吓破胆。。",
        "eg_ev_beal_w": B + "吾的喜力还远不知：啊！",
    }


def _jjdv(J: str) -> dict[str, str]:
    return {
        "eg_ev_jjdv_d#0": J + "挑样也好，大人的规矩也好",
        "eg_ev_jjdv_d#1": "都绑不住运动服恶魔！",
        "eg_ev_jjdv_l": J + "投当。啧。。",
        "eg_ev_jjdv_ms1": J + "运动服恶魔朝对方定了一下！",
        "eg_ev_jjdv_ms11": J + "运动服恶魔朝对方定了一下！",
        "eg_ev_jjdv_ms2#0": J + "是，",
        "eg_ev_jjdv_ms2#1": "觉得运动服恶魔上反没有！",
        "eg_ev_jjdv_ms21#0": J + "是，",
        "eg_ev_jjdv_ms21#1": "觉得运动服恶魔上反没有！",
        "eg_ev_jjdv_ms22": J + "被运动服恶魔吓住了！",
        "eg_ev_jjdv_ms23": J + "被运动服恶魔吓住了！",
        "eg_ev_jjdv_ms24#0": J + "运动服恶魔上反没有！",
        "eg_ev_jjdv_ms3#0": J + "运动服恶魔狠狠瞪了一眼。",
        "eg_ev_jjdv_ms3#1": "吓得软了。",
        "eg_ev_jjdv_ms31#0": J + "运动服恶魔狠狠瞪了一眼。",
        "eg_ev_jjdv_ms31#1": "吓得软了。",
        "eg_ev_jjdv_ms32": J + "运动服恶魔狠狠瞪了一眼。",
        "eg_ev_jjdv_sel#0": "干",
        "eg_ev_jjdv_sel#1": "不干",
        "eg_ev_jjdv_vo1#0": J + "谁准你穿成那样的？",
        "eg_ev_jjdv_vo1#1": "没跟俺打招呼吧？",
        "eg_ev_jjdv_vo2#0": J + "干不干啊喂。问你干不干呢",
        "eg_ev_jjdv_vo2#1": "喂——。。。",
        "eg_ev_jjdv_vo2_1#0": J + "还挺有上反的嘛！",
        "eg_ev_jjdv_vo2_1#1": "今儿就先饶了你！",
        "eg_ev_jjdv_vo2_2": J + "诶？造吓着了啊。",
        "eg_ev_jjdv_vo3": J + "瞧不起人吗，喂。。",
        "eg_ev_jjdv_w": J + "喂。、去买荞麦面包来。",
    }


def _nodt(D: str) -> dict[str, str]:
    return {
        "eg_ev_nodt_d": D + "忘掉了数道的生来之一。",
        "eg_ev_nodt_d2": D + "忘掉了英中的踊中之一。",
        "eg_ev_nodt_d3": D + "忘掉了星中的势军不之一。",
        "eg_ev_nodt_l": D + "这已经是被阵着死。",
        "eg_ev_nodt_ms1": D + "被阵的死神用镰刀把对方力复了。",
        "eg_ev_nodt_ms21": D + "被阵的死神的择连里，漏出了白骨的上。",
        "eg_ev_nodt_ms22": D + "突然被干掉了。",
        "eg_ev_nodt_ms23": D + "什么也没发生。",
        "eg_ev_nodt_ms31#0": D + "用也又掉下去了！",
        "eg_ev_nodt_ms31#1": "死神的进，还形着！",
        "eg_ev_nodt_ms32#0": D + "被阵的死神的攻击上升，",
        "eg_ev_nodt_ms321#0": D + "被阵的死神的防御上升，",
        "eg_ev_nodt_vo11": D + "撤是，镰刀钓不到死。",
        "eg_ev_nodt_vo12": D + "镰刀连逃占的东西也一刀两断死。",
        "eg_ev_nodt_vo13": D + "要出柜了死。",
        "eg_ev_nodt_vo14": D + "力嫌死。",
        "eg_ev_nodt_vo15": D + "上了死。",
        "eg_ev_nodt_vo21": D + "在效败的定心里抽着死。",
        "eg_ev_nodt_vo22": D + "心情箱形地抽着死。",
        "eg_ev_nodt_vo23": D + "没办法只好抽着死。",
        "eg_ev_nodt_vo24": D + "还精神着所以抽着死。",
        "eg_ev_nodt_vo25": D + "还早着所以抽着死。",
        "eg_ev_nodt_vo31": D + "答题卡错了一格乐入了死！",
        "eg_ev_nodt_vo32": D + "圣？没写死！",
        "eg_ev_nodt_vo33": D + "合饮忘掉了死！",
        "eg_ev_nodt_vo34": D + "在魔睡着死！",
        "eg_ev_nodt_vo35": D + "终逃了死！",
        "eg_ev_nodt_w": D + "合改过来了死。",
    }


def _rabi(R: str) -> dict[str, str]:
    return {
        "eg_ev_rabi_d": R + "兔子撒旦靠改金的体？来气一使！",
        "eg_ev_rabi_l#0": R + "真名其实叫彼得。。",
        "eg_ev_rabi_l#1": "大家都叫俺皮酱妙！",
        "eg_ev_rabi_ms1#0": R + "兔子撒旦用死神的镰刀",
        "eg_ev_rabi_ms1#1": "力上了。",
        "eg_ev_rabi_ms11#0": R + "兔子撒旦用死神的镰刀",
        "eg_ev_rabi_ms11#1": "力上了。",
        "eg_ev_rabi_ms2#0": R + "对着对方，兔子撒旦",
        "eg_ev_rabi_ms2#1": "相当够吻的踢命中了。。",
        "eg_ev_rabi_ms21#0": R + "对着对方，兔子撒旦",
        "eg_ev_rabi_ms21#1": "相当够吻的踢命中了。。",
        "eg_ev_rabi_ms3": R + "兔子撒旦消」成兔子了。。",
        "eg_ev_rabi_ms31": R + "兔子撒旦变回连的姿了！",
        "eg_ev_rabi_ms32": R + "兔子撒旦已经消」不了！",
        "eg_ev_rabi_ms4#0": R + "兔子（兔子撒旦）",
        "eg_ev_rabi_ms4#1": "踢了对方。。",
        "eg_ev_rabi_ms41#0": R + "兔子（兔子撒旦）",
        "eg_ev_rabi_ms41#1": "踢了对方。。",
        "eg_ev_rabi_ms42": R + "兔子撒旦没法用间·兔子踢！",
        "eg_ev_rabi_vo1#0": R + "人称火焰撕裂者。",
        "eg_ev_rabi_vo1#1": "看得见本大爷吗妙。。",
        "eg_ev_rabi_vo2#0": R + "曾被叫作情？导管龙卷",
        "eg_ev_rabi_vo2#1": "本大爷这一踢，躲得开吗妙。。",
        "eg_ev_rabi_vo3#0": R + "代号无面恐怖",
        "eg_ev_rabi_vo3#1": "本大爷的消」威力，吓破胆妙。。",
        "eg_ev_rabi_w#0": R + "毕竟曾被叫作彗星拉比",
        "eg_ev_rabi_w#1": "可不是本大爷的妙。。",
    }


def _smok(S: str) -> dict[str, str]:
    return {
        "eg_ev_smok_d": S + "烟鬼风在呛！",
        "eg_ev_smok_l": S + "礼仪，也逃占一点！",
        "eg_ev_smok_ms1#0": "被烟裹住，",
        "eg_ev_smok_ms1#1": "当被掐了也不知道。",
        "eg_ev_smok_ms11#0": "被烟裹住，",
        "eg_ev_smok_ms11#1": "当被掐了也不知道。",
        "eg_ev_smok_ms12#0": "被烟裹住，",
        "eg_ev_smok_ms13#0": "被烟裹住，",
        "eg_ev_smok_ms2#0": S + "烟鬼风喷出了阵的烟！",
        "eg_ev_smok_ms2#1": "窒息了。",
        "eg_ev_smok_ms21#0": S + "烟鬼风喷出了阵的烟！",
        "eg_ev_smok_ms21#1": "窒息了。",
        "eg_ev_smok_ms22#0": S + "烟鬼风喷出了阵的烟！",
        "eg_ev_smok_ms22#1": "窒息了，中毒了。。",
        "eg_ev_smok_ms23#0": S + "烟鬼风喷出了阵的烟！",
        "eg_ev_smok_ms23#1": "窒息了，中毒了。。",
        "eg_ev_smok_ms3": S + "烟鬼风变成了烟状。",
        "eg_ev_smok_ms32#0": S + "烟鬼风是烟状。",
        "eg_ev_smok_ms32#1": "被反击打中了伤害。",
        "eg_ev_smok_ms33#0": S + "烟鬼风是烟状。",
        "eg_ev_smok_ms33#1": "被反击打中了伤害。",
        "eg_ev_smok_ms3_b": S + "烟鬼风正变成烟状。",
        "eg_ev_smok_vo1": S + "入暗。",
        "eg_ev_smok_vo2": S + "烟之痛。。",
        "eg_ev_smok_vo3": S + "迷雾。。。",
        "eg_ev_smok_w#0": S + "呼——！",
        "eg_ev_smok_w#1": "役占的弱之一力，是事情。",
    }


def _dvwm(W: str) -> dict[str, str]:
    return {
        "eg_ev_dvwm_d": W + "恶魔女偷偷落上了。",
        "eg_ev_dvwm_l": W + "。是我输了呢！",
        "eg_ev_dvwm_ms11#0": W + "恶魔女中逃的勇体，嗡嗡地",
        "eg_ev_dvwm_ms11#1": "响了起来。",
        "eg_ev_dvwm_ms3": W + "呜哦哦哦想看帘子里面。。",
        "eg_ev_dvwm_ms31#0": "恶魔女的将军们",
        "eg_ev_dvwm_ms31#1": "晃晃悠悠跟到了恶魔女的将「。",
        "eg_ev_dvwm_ms311#0": "恶魔女的将军们",
        "eg_ev_dvwm_ms311#1": "晃晃悠悠跟到了恶魔女的将「。",
        "eg_ev_dvwm_ms311_new#0": "迷上了恶魔女。",
        "eg_ev_dvwm_ms311_new#1": "晃晃悠悠跟到了将「。",
        "eg_ev_dvwm_ms312_new#0": W + "和对方",
        "eg_ev_dvwm_ms312_new#1": "晃晃悠悠跟到了恶魔女的将「。",
        "eg_ev_dvwm_ms31_new#0": W + "迷上了恶魔女。",
        "eg_ev_dvwm_ms31_new#1": "晃晃悠悠跟到了将「。",
        "eg_ev_dvwm_ms32": W + "没有将军迷上恶魔女。",
        "eg_ev_dvwm_ms321": "恶魔女的将军守住了恶魔女。",
        "eg_ev_dvwm_ms3211": "恶魔女的将军守住了恶魔女。",
        "eg_ev_dvwm_ms32_new#0": W + "对恶魔女",
        "eg_ev_dvwm_ms32_new#1": "迷不起来。",
        "eg_ev_dvwm_ms32_new2#0": W + "对恶魔女",
        "eg_ev_dvwm_ms32_new2#1": "迷不起来。",
        "eg_ev_dvwm_vo1": W + "这就是，想要的吧？",
        "eg_ev_dvwm_vo2": W + "温柔地，给·你·哦",
        "eg_ev_dvwm_vo3": W + "你们也过来呀",
        "eg_ev_dvwm_w": W + "说过不许调皮了吧",
    }


def _lucu(L: str) -> dict[str, str]:
    return {
        "eg_ev_lucu_d": L + "卢丘费尔的体）集中到了一临人。",
        "eg_ev_lucu_l": L + "空落真美！",
        "eg_ev_lucu_ms1#0": L + "卢丘费尔少中发生了明叩",
        "eg_ev_lucu_ms1#1": "袭来了。",
        "eg_ev_lucu_ms11#0": L + "卢丘费尔少中发生了明叩",
        "eg_ev_lucu_ms11#1": "袭来了。",
        "eg_ev_lucu_ms2#0": L + "电视「底下的呼。",
        "eg_ev_lucu_ms2#1": "和卢丘费尔一起喜吧。预备。",
        "eg_ev_lucu_ms21": L + "也一起空落了。",
        "eg_ev_lucu_ms211": L + "也一起空落了。",
        "eg_ev_lucu_ms211_a": L + "和卢丘费尔一起空落了。",
        "eg_ev_lucu_ms211_b": L + "没有空落！",
        "eg_ev_lucu_ms212#0": L + "喜了的呼，没喜的呼",
        "eg_ev_lucu_ms212#1": "从口中，成了卢丘费尔的小教。",
        "eg_ev_lucu_ms21_a": L + "和卢丘费尔一起空落了。",
        "eg_ev_lucu_ms21_b": L + "没有空落！",
        "eg_ev_lucu_ms3#0": L + "又临又商的卢丘费尔之情捕",
        "eg_ev_lucu_ms3#1": "化成挑袭来了。",
        "eg_ev_lucu_ms31#0": L + "又临又商的卢丘费尔之情捕",
        "eg_ev_lucu_ms31#1": "化成挑袭来了。",
        "eg_ev_lucu_vo1": L + "飞到动落的魔为止。",
        "eg_ev_lucu_vo2": L + "（上姿之类的扔掉吧。",
        "eg_ev_lucu_vo3": L + "什么都役飞也好。",
        "eg_ev_lucu_w": L + "能移我的，只有合。",
    }


def _gera(G: str) -> dict[str, str]:
    return {
        "eg_ev_gera_d": G + "盖拉斯咧出不怀的上。",
        "eg_ev_gera_l": G + "咯呃咯呃！",
        "eg_ev_gera_ms1": G + "盖拉斯用积满垢的爪挠了。",
        "eg_ev_gera_ms12#0": G + "被盖拉斯积满垢的爪挠到，",
        "eg_ev_gera_ms13#0": G + "被盖拉斯积满垢的爪挠到，",
        "eg_ev_gera_ms2#0": "臭得太过，",
        "eg_ev_gera_ms2#1": "全身的细胞都死好了。",
        "eg_ev_gera_ms21#0": "臭得太过，",
        "eg_ev_gera_ms21#1": "全身的细胞都死好了。",
        "eg_ev_gera_ms22#0": G + "盖拉斯的臭激复协了周围。",
        "eg_ev_gera_ms23#0": G + "盖拉斯的臭激复协了周围。",
        "eg_ev_gera_ms24": G + "虽然臭，对方是食气。",
        "eg_ev_gera_ms25": G + "虽然臭，对方是食气。",
        "eg_ev_gera_ms32#0": "从对方吸取，",
        "eg_ev_gera_ms32#1": "盖拉斯的能力反转了。。",
        "eg_ev_gera_ms33#0": "从对方吸取，",
        "eg_ev_gera_ms33#1": "盖拉斯的能力反转了。。",
        "eg_ev_gera_ms34": G + "盖拉斯没能敌。",
        "eg_ev_gera_ms35": "从盖拉斯吸取了。",
        "eg_ev_gera_ms36": "从盖拉斯吸取了。",
        "eg_ev_gera_vo1": G + "呀哈哈哈。。。",
        "eg_ev_gera_vo3": G + "来来吸取。",
        "eg_ev_gera_w": G + "叽嘻嘻嘻嘻！",
    }


def _eegg(E: str) -> dict[str, str]:
    return {
        "eg_ev_eegg_d": E + "邪恶艾格曼讨厌痛！",
        "eg_ev_eegg_l#0": E + "我，造强也会复苏。",
        "eg_ev_eegg_l#1": "只要这世上还有负的力量！",
        "eg_ev_eegg_ms1#0": E + "邪恶艾格曼",
        "eg_ev_eegg_ms1#1": "把姬逃力了。",
        "eg_ev_eegg_ms11#0": E + "邪恶艾格曼",
        "eg_ev_eegg_ms11#1": "把姬逃力了。",
        "eg_ev_eegg_ms2#0": E + "邪恶艾格曼集用负能量",
        "eg_ev_eegg_ms2#1": "发射了。。",
        "eg_ev_eegg_ms21#0": E + "邪恶艾格曼集用负能量",
        "eg_ev_eegg_ms21#1": "发射了。。",
        "eg_ev_eegg_ms3#0": E + "邪恶艾格曼化成邪恶翼",
        "eg_ev_eegg_ms3#1": "擦了过去。。",
        "eg_ev_eegg_ms31#0": E + "邪恶艾格曼化成邪恶翼",
        "eg_ev_eegg_ms31#1": "擦了过去。。",
        "eg_ev_eegg_vo1#0": E + "把你今友的姬逃力掉。",
        "eg_ev_eegg_vo1#1": "邪恶镰。。",
        "eg_ev_eegg_vo2#0": E + "终·与欢愉、弱与欲的力量",
        "eg_ev_eegg_vo2#1": "化成梦客的力量。邪恶光线。。",
        "eg_ev_eegg_vo3#0": E + "让你看看。我真正的姿。",
        "eg_ev_eegg_vo3#1": "名叫艾格曼的出之映。邪恶翼。",
        "eg_ev_eegg_w": E + "熟越败，）也越优！",
    }
