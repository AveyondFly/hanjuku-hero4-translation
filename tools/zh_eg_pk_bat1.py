"""Pink-egg battle lines A (ripn–bbms)."""
from __future__ import annotations


def by_id() -> dict[str, str]:
    L = "唇骑士："
    I = "透明人："
    H = "许德拉："
    P = "粉红艾格曼："
    A = "气之使者："
    G = "格特鲁德："
    M = "捕获他组："
    K = "米尔基："
    B = "宝宝蛾："
    out: dict[str, str] = {}
    out.update(_ripn(L))
    out.update(_tmni(I))
    out.update(_hydr(H))
    out.update(_pegg(P))
    out.update(_aiss(A))
    out.update(_gtrd(G))
    out.update(_musu(M))
    out.update(_milk(K))
    out.update(_bbms(B))
    return out


def _ripn(L: str) -> dict[str, str]:
    suck = L + "是要把一切吸干的吻！"
    out = {
        "eg_pk_ripn_d": L + "唇骑士裂开了！",
        "eg_pk_ripn_l": L + "比尔，给临终之吻嘛",
        "eg_pk_ripn_ms1#0": L + "唇骑士和对方",
        "eg_pk_ripn_ms1#1": "用嘴唇对上气了！",
        "eg_pk_ripn_ms11#0": L + "唇骑士和对方",
        "eg_pk_ripn_ms11#1": "用嘴唇对上气了！",
        "eg_pk_ripn_ms2#0": L + "唇骑士把鲜红的口红厚厚涂上了！",
        "eg_pk_ripn_ms2#1": "攻击和防御上升了。。",
        "eg_pk_ripn_ms32_b": L + "把对方的一切吸干了。",
        "eg_pk_ripn_ms32_c": L + "把对方的一切吸干了。",
        "eg_pk_ripn_vo1#0": L + "比尔，我们的气不需要始叶哦！",
        "eg_pk_ripn_vo1#1": "用唇对唇对上嘛",
        "eg_pk_ripn_vo2": L + "哈，红唇膏才是战场力哦",
        "eg_pk_ripn_vo3#0": L + "啊啊，比尔，想要你的一切！",
        "eg_pk_ripn_vo3#1": "嘴唇在发烫哦",
        "eg_pk_ripn_w": L + "哎呀讨厌，细看你也不是比尔呢？",
    }
    pairs = {
        "ms3": "的能力和威力吸走了。。",
        "ms32": "的能力和威力吸走了。。",
        "ms32_atk": "的能力和攻击吸走了。。",
        "ms32_def": "的能力和防御吸走了。。",
        "ms32_men": "的能力和精神吸走了。。",
        "ms32_spd": "的能力和速度吸走了。。",
        "ms33_atk": "的攻击吸走了。。",
        "ms33_def": "的防御吸走了。。",
        "ms33_men": "的精神吸走了。。",
        "ms33_spd": "的速度吸走了。。",
        "ms34_atk": "的攻击吸走了。。",
        "ms34_def": "的防御吸走了。。",
        "ms34_men": "的精神吸走了。。",
        "ms34_spd": "的速度吸走了。。",
        "ms3_atk": "的能力和攻击吸走了。。",
        "ms3_def": "的能力和防御吸走了。。",
        "ms3_men": "的能力和精神吸走了。。",
        "ms3_spd": "的能力和速度吸走了。。",
    }
    for key, line in pairs.items():
        out[f"eg_pk_ripn_{key}#0"] = suck
        out[f"eg_pk_ripn_{key}#1"] = line
    return out


def _tmni(I: str) -> dict[str, str]:
    return {
        "eg_pk_tmni_d": I + "虽然不知道打到哪儿了。",
        "eg_pk_tmni_l": I + "对不起啦。",
        "eg_pk_tmni_ms11": I + "透明人在对方脸上涂鸦了。",
        "eg_pk_tmni_ms112": I + "透明人在对方脸上涂鸦了。",
        "eg_pk_tmni_ms12": I + "决定把脸露出来统一。",
        "eg_pk_tmni_ms122": I + "决定把脸露出来统一。",
        "eg_pk_tmni_ms123": I + "还没发觉。",
        "eg_pk_tmni_ms124": I + "还没发觉。",
        "eg_pk_tmni_ms21#0": I + "透明人把对方的反",
        "eg_pk_tmni_ms21#1": "胳肢了一下。",
        "eg_pk_tmni_ms212#0": I + "透明人把对方的反",
        "eg_pk_tmni_ms212#1": "胳肢了一下。",
        "eg_pk_tmni_ms22#0": I + "痒得太过，攻击",
        "eg_pk_tmni_ms22#1": "忘掉了。",
        "eg_pk_tmni_ms222#0": I + "痒得太过，攻击",
        "eg_pk_tmni_ms222#1": "忘掉了。",
        "eg_pk_tmni_ms23": I + "没痒到番。。",
        "eg_pk_tmni_ms232": I + "没痒到番。。",
        "eg_pk_tmni_ms24": I + "有一点点痒！",
        "eg_pk_tmni_ms242": I + "有一点点痒！",
        "eg_pk_tmni_ms31#0": I + "透明人把对方部队将军",
        "eg_pk_tmni_ms31#1": "撞了个满怀。",
        "eg_pk_tmni_ms312#0": I + "透明人把对方部队将军",
        "eg_pk_tmni_ms312#1": "撞了个满怀。",
        "eg_pk_tmni_ms32#0": I + "透明人想把对方将军小军",
        "eg_pk_tmni_ms32#1": "撞满怀，可是不在，放弃了。",
        "eg_pk_tmni_ms322#0": I + "透明人想把对方将军小军",
        "eg_pk_tmni_ms322#1": "撞满怀，可是不在，放弃了。",
        "eg_pk_tmni_vo1": I + "看不见啦。",
        "eg_pk_tmni_vo2": I + "胳肢一下啦。",
        "eg_pk_tmni_vo3": I + "要骗人，先从活食开始啦。",
        "eg_pk_tmni_w": I + "恶作剧合好啦。",
    }


def _hydr(H: str) -> dict[str, str]:
    return {
        "eg_pk_hydr_d": H + "许德拉来气了。",
        "eg_pk_hydr_l": H + "究竟。中不起来。",
        "eg_pk_hydr_ms1#0": H + "许德拉的身体砸向对方，",
        "eg_pk_hydr_ms1#1": "操被收了。",
        "eg_pk_hydr_ms11#0": H + "许德拉的身体砸向对方，",
        "eg_pk_hydr_ms11#1": "操被收了。",
        "eg_pk_hydr_ms12": H + "晕乎乎的。",
        "eg_pk_hydr_ms13": H + "晕乎乎的。",
        "eg_pk_hydr_ms2#0": H + "朝对方（去，",
        "eg_pk_hydr_ms2#1": "吻得状水花溅了上来。",
        "eg_pk_hydr_ms21#0": H + "朝对方（去，",
        "eg_pk_hydr_ms21#1": "吻得状水花溅了上来。",
        "eg_pk_hydr_ms22#0": H + "朝大家（去，",
        "eg_pk_hydr_ms22#1": "吻得状水花溅了上来。",
        "eg_pk_hydr_ms23#0": H + "朝大家（去，",
        "eg_pk_hydr_ms23#1": "吻得状水花溅了上来。",
        "eg_pk_hydr_ms32#0": H + "像是在和看不见的造",
        "eg_pk_hydr_ms32#1": "打着仗。",
        "eg_pk_hydr_ms321#0": H + "像是在和看不见的造",
        "eg_pk_hydr_ms321#1": "打着仗。",
        "eg_pk_hydr_ms33": H + "喜欢思场的食。",
        "eg_pk_hydr_ms331": H + "喜欢思场的食。",
        "eg_pk_hydr_ms332#0": H + "许德拉的场敌有让人看见幻觉的效果。",
        "eg_pk_hydr_ms332#1": "被迷惑了！",
        "eg_pk_hydr_ms333#0": H + "许德拉的场敌有让人看见幻觉的效果。",
        "eg_pk_hydr_ms333#1": "被迷惑了！",
        "eg_pk_hydr_vo1": H + "紧紧抱住哦！呐？可以吧？",
        "eg_pk_hydr_vo2": H + "状蛇许德拉别靠近看。",
        "eg_pk_hydr_vo3": H + "啦啦啦，大家都在打哟",
        "eg_pk_hydr_w": H + "呜呼呼，是我赢了呢。",
    }


def _pegg(P: str) -> dict[str, str]:
    return {
        "eg_pk_pegg_d#0": P + "粉红艾格曼",
        "eg_pk_pegg_d#1": "咬紧牙关忍着痛！",
        "eg_pk_pegg_l": P + "那、那样。呀啊啊——。",
        "eg_pk_pegg_ms1#0": P + "粉红艾格曼的造气爆发，",
        "eg_pk_pegg_ms1#1": "也一起飞出去了。",
        "eg_pk_pegg_ms11#0": P + "粉红艾格曼的造气爆发，",
        "eg_pk_pegg_ms11#1": "也一起飞出去了。",
        "eg_pk_pegg_ms2#0": P + "粉红艾格曼把绷紧的弦解开了。。",
        "eg_pk_pegg_ms2#1": "严厉的／扎了进去。。",
        "eg_pk_pegg_ms21#0": P + "粉红艾格曼把绷紧的弦解开了。。",
        "eg_pk_pegg_ms21#1": "严厉的／扎了进去。。",
        "eg_pk_pegg_ms3#0": P + "粉红艾格曼把飞」悄悄亮了一下。",
        "eg_pk_pegg_ms3#1": "逃挑立。。",
        "eg_pk_pegg_ms31#0": P + "粉红艾格曼把飞」悄悄亮了一下。",
        "eg_pk_pegg_ms31#1": "逃挑立。。",
        "eg_pk_pegg_ms32#0": P + "粉红艾格曼把飞」悄悄亮了一下。",
        "eg_pk_pegg_ms32#1": "对方完全不在乎！",
        "eg_pk_pegg_ms33#0": P + "粉红艾格曼把飞」悄悄亮了一下。",
        "eg_pk_pegg_ms33#1": "对方完全不在乎！",
        "eg_pk_pegg_vo1#0": P + "会在心上开个洞哦。繰",
        "eg_pk_pegg_vo1#1": "粉红炸弹。",
        "eg_pk_pegg_vo2#0": P + "绷紧的弦，会把心部拔掉哦",
        "eg_pk_pegg_vo2#1": "粉红樱桃。",
        "eg_pk_pegg_vo3": P + "呜呼，这样如何？",
        "eg_pk_pegg_w": P + "就算这样，也别靠近看哦",
    }


def _aiss(A: str) -> dict[str, str]:
    return {
        "eg_pk_aiss_d": A + "星逃力不力连。气之使者看起来想要。",
        "eg_pk_aiss_l": A + "气竟是如此艰难！",
        "eg_pk_aiss_ms12#0": A + "除了战斗别无展现威大的食小",
        "eg_pk_aiss_ms12#1": "的火，猛地痛了。",
        "eg_pk_aiss_ms121#0": A + "除了战斗别无展现威大的食小",
        "eg_pk_aiss_ms121#1": "的火，猛地痛了。",
        "eg_pk_aiss_ms2#0": A + "把火拔摇的界森",
        "eg_pk_aiss_ms2#1": "打中了对方的火。",
        "eg_pk_aiss_ms21#0": A + "把火拔摇的界森",
        "eg_pk_aiss_ms21#1": "打中了对方的火。",
        "eg_pk_aiss_ms22": A + "和气之使者先互相勒着。。",
        "eg_pk_aiss_ms23": A + "从气之使者的气里被解开了。。",
        "eg_pk_aiss_ms24": A + "和气之使者先互相勒着。。",
        "eg_pk_aiss_ms25": A + "从气之使者的气里被解开了。。",
        "eg_pk_aiss_ms32#0": A + "被气包住，",
        "eg_pk_aiss_ms32#1": "明显睡着了！",
        "eg_pk_aiss_ms321#0": A + "被气包住，",
        "eg_pk_aiss_ms321#1": "明显睡着了！",
        "eg_pk_aiss_ms322": A + "感到了气。",
        "eg_pk_aiss_ms323": A + "感到了气。",
        "eg_pk_aiss_vo1": A + "神圣的气啊。到这里来。",
        "eg_pk_aiss_vo2": A + "正在气着。",
        "eg_pk_aiss_vo3": A + "停下战斗，来气定吧。",
        "eg_pk_aiss_w": A + "把气和地中在一起。",
    }


def _gtrd(G: str) -> dict[str, str]:
    return {
        "eg_pk_gtrd_d": G + "格特鲁德把所有的气都接下来！",
        "eg_pk_gtrd_l#0": G + "把我忘了去当大人吧",
        "eg_pk_gtrd_l#1": "再见！",
        "eg_pk_gtrd_ms1#0": G + "格特鲁德在战入里找到了小小的气！",
        "eg_pk_gtrd_ms1#1": "对对方来说是逃」！",
        "eg_pk_gtrd_ms11#0": G + "格特鲁德在战入里找到了小小的气！",
        "eg_pk_gtrd_ms11#1": "对对方来说是逃」！",
        "eg_pk_gtrd_ms2": G + "莫名其妙被扇了一巴掌！",
        "eg_pk_gtrd_ms21": G + "莫名其妙被扇了一巴掌！",
        "eg_pk_gtrd_ms22#0": G + "分别，若不是一强把爱使军过的弱",
        "eg_pk_gtrd_ms22#1": "是无法使军的！",
        "eg_pk_gtrd_ms3": G + "格特鲁德的气是本星。。",
        "eg_pk_gtrd_ms32#0": G + "启程，若不是一强把分别使军过的弱",
        "eg_pk_gtrd_ms32#1": "是无法使军的！",
        "eg_pk_gtrd_vo1#0": G + "什么什么？这能的心跳是！",
        "eg_pk_gtrd_vo1#1": "难道这就是气——。",
        "eg_pk_gtrd_vo2#0": G + "好、好过分啊我。食居然是小军",
        "eg_pk_gtrd_vo2#1": "是在玩弄我呢。",
        "eg_pk_gtrd_vo3#0": G + "我，出？。为了忘掉食而出？！",
        "eg_pk_gtrd_vo3#1": "不行。不行。。忘掉食这种事做不到！",
        "eg_pk_gtrd_vo3_a": G + "我，出？。为了忘掉食而出？！",
        "eg_pk_gtrd_vo3_b": G + "不行。不行。。忘掉食这种事做不到！",
        "eg_pk_gtrd_w#0": G + "啊啊。怎么会这样。",
        "eg_pk_gtrd_w#1": "我气着。把食打倒了呢！",
    }


def _musu(M: str) -> dict[str, str]:
    return {
        "eg_pk_musu_d": M + "捕获他组的魔坏力出了置。",
        "eg_pk_musu_l": M + "捕获他组解入，大家都待姬了！",
        "eg_pk_musu_ms11": M + "捕获他组在巴咪的地方降了起来。",
        "eg_pk_musu_ms12": M + "定「和守心在一起，那个吻引发了地。",
        "eg_pk_musu_ms21": M + "捕获他组连着协，给自己打气。",
        "eg_pk_musu_ms22": M + "捕获他组的攻击上升了。。",
        "eg_pk_musu_ms23": M + "捕获他组的防御上升了。。",
        "eg_pk_musu_ms24": M + "捕获他组的速度上升了。。",
        "eg_pk_musu_ms25": M + "捕获他组的精神上升了。。",
        "eg_pk_musu_ms31": M + "三人里，最喜欢哪一个？",
        "eg_pk_musu_ms32": M + "好。猜中。送出了逃爆发。",
        "eg_pk_musu_ms33#0": M + "没猜中，挨了爆发。",
        "eg_pk_musu_ms33#1": "受到100点伤害。。",
        "eg_pk_musu_ms331#0": M + "没猜中，挨了爆发。",
        "eg_pk_musu_ms331#1": "受到100点伤害。。",
        "eg_pk_musu_ms331_b#0": M + "没猜中，挨了爆发。",
        "eg_pk_musu_ms331_b#1": "100点伤害。。",
        "eg_pk_musu_ms34": M + "奥斯卡！造也做不到！",
        "eg_pk_musu_msel#0": "能的他",
        "eg_pk_musu_msel#1": "中间的他",
        "eg_pk_musu_msel#2": "守的他",
        "eg_pk_musu_msel_2#0": "能的他",
        "eg_pk_musu_msel_2#2": "守的他",
        "eg_pk_musu_w": M + "捕获他组正可着直播的弱半。",
    }


def _milk(K: str) -> dict[str, str]:
    return {
        "eg_pk_milk_d": K + "米尔基在晃悠晃悠。",
        "eg_pk_milk_l": K + "要变成酸奶之前，都会加油的！",
        "eg_pk_milk_ms1": K + "米尔基把叶客喝超，能力反转了。。",
        "eg_pk_milk_ms21": K + "让弱分梦兄字的米尔基奶喝了一升。",
        "eg_pk_milk_ms22#0": K + "啊。喝多了。",
        "eg_pk_milk_ms22#1": "肚子咕噜咕噜了。",
        "eg_pk_milk_ms221#0": K + "啊。喝多了。",
        "eg_pk_milk_ms221#1": "肚子咕噜咕噜了。",
        "eg_pk_milk_ms222": K + "的肚子，是食气。",
        "eg_pk_milk_ms223": K + "的肚子，是食气。",
        "eg_pk_milk_ms224#0": K + "好喝的叶客。",
        "eg_pk_milk_ms225#0": K + "好喝的叶客。",
        "eg_pk_milk_ms3": K + "米尔基喊着缺钙。",
        "eg_pk_milk_ms3#0": K + "米尔基很温和。",
        "eg_pk_milk_ms3#1": "不是会突然爆发的那种。。",
        "eg_pk_milk_vo1": K + "好。把手放在腰上。",
        "eg_pk_milk_vo12": K + "咕嘟咕嘟咕嘟（喝叶客状）",
        "eg_pk_milk_vo13": K + "米尔基奶，日也连气。",
        "eg_pk_milk_vo2#0": K + "那么焦躁，是缺钙呢。",
        "eg_pk_milk_vo2#1": "来，你也米尔基奶",
        "eg_pk_milk_vo3#0": K + "爱喝奶的我的钙，",
        "eg_pk_milk_vo3#1": "哞。到客界了哦。。",
        "eg_pk_milk_w": K + "金日连气，米尔基奶",
    }


def _bbms(B: str) -> dict[str, str]:
    return {
        "eg_pk_bbms_d": B + "宝宝蛾在鼓着脸。",
        "eg_pk_bbms_l": B + "宝宝蛾半靠着（走了！",
        "eg_pk_bbms_ms11": B + "宝宝蛾骨碌骨碌骨碌地箱了。",
        "eg_pk_bbms_ms12#0": "撞到宝宝蛾的脚，却被轻轻摸了摸，",
        "eg_pk_bbms_ms12#1": "满心只想再来。",
        "eg_pk_bbms_ms121#0": "撞到宝宝蛾的脚，却被轻轻摸了摸，",
        "eg_pk_bbms_ms121#1": "满心只想再来。",
        "eg_pk_bbms_ms2#0": B + "有点弱的宝宝，）·地效着",
        "eg_pk_bbms_ms2#1": "速度下降。",
        "eg_pk_bbms_ms21#0": B + "宝宝，「想要吗？",
        "eg_pk_bbms_ms21#1": "真拿这淘气精没办法攻",
        "eg_pk_bbms_ms22#0": B + "有点弱的宝宝，）·地效着",
        "eg_pk_bbms_ms22#1": "速度下降。",
        "eg_pk_bbms_ms23": B + "要成为立力的大人哦，宝宝",
        "eg_pk_bbms_ms31#0": B + "土脚啪嗒啪嗒，在逃逃。",
        "eg_pk_bbms_ms31#1": "求你挨一下行不行？",
        "eg_pk_bbms_ms32#0": B + "居然挨了一下。",
        "eg_pk_bbms_ms32#1": "还挺好的家伙嘛。",
        "eg_pk_bbms_ms321#0": B + "居然挨了一下。",
        "eg_pk_bbms_ms321#1": "还挺好的家伙嘛。",
        "eg_pk_bbms_w#0": B + "宝宝蛾根本没觉得对手输了",
        "eg_pk_bbms_w#1": "正可着梦大气。",
    }
