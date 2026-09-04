"""Dungeon common UI, warp menus, China merchant, homeless, seals. Tekken skipped."""
from __future__ import annotations


def _warp_menus() -> dict[str, str]:
    out: dict[str, str] = {}
    for n in range(1, 10):
        for i, floor in enumerate(range(n, 0, -1)):
            out[f"dg_common_WarpChoose{n:02d}#{i}"] = f"第{floor}层"
        out[f"dg_common_WarpChoose{n:02d}#{n}"] = "取消"
    out["dg_common_WarpChoose10#0"] = "最终层"
    for i, floor in enumerate(range(9, 0, -1), start=1):
        out[f"dg_common_WarpChoose10#{i}"] = f"第{floor}层"
    out["dg_common_WarpChoose10#10"] = "取消"
    out["dg_common_WarpChoose_next1#0"] = "去最初一层"
    out["dg_common_WarpChoose_next1#1"] = "取消"
    out["dg_common_WarpChoose_next2#0"] = "去最初一层"
    out["dg_common_WarpChoose_next2#1"] = "去途中一层"
    out["dg_common_WarpChoose_next2#2"] = "取消"
    out["dg_common_WarpChoose_next3#0"] = "去途中一层"
    out["dg_common_WarpChoose_next3#1"] = "取消"
    levels = {
        1: (6,),
        2: (11, 15),
        3: (21, 26),
        4: (31, 36),
        5: (41, 46),
        6: (51, 56),
        7: (61, 65),
        8: (71, 76),
        9: (81, 86),
        10: (91, 97),
    }
    for n, floors in levels.items():
        out[f"dg_common_WarpChoose_next_level{n}#0"] = f"去地下{floors[0]}层"
        out[f"dg_common_WarpChoose_next_level{n}#1"] = "取消"
        if len(floors) == 2:
            out[f"dg_common_WarpChoose_next_level{n}_2#0"] = f"去地下{floors[0]}层"
            out[f"dg_common_WarpChoose_next_level{n}_2#1"] = f"去地下{floors[1]}层"
            out[f"dg_common_WarpChoose_next_level{n}_2#2"] = "取消"
    return out


def by_id() -> dict[str, str]:
    CH = "华人："
    HM = "流浪汉："
    out: dict[str, str] = {
        "dg_common_Actor": "搭话",
        "dg_common_Box": "宝箱",
        "dg_common_BoxChoose#0": "打开",
        "dg_common_BoxChoose#1": "算了",
        "dg_common_BoxMsg": "用小钥匙打开宝箱吗？",
        "dg_common_BoxMsgCannot": "没有小钥匙，打不开宝箱",
        "dg_common_BoxMsgEnough": "宝袋已满，打不开宝箱",
        "dg_common_CanWarp#0": "被封印的门：能走到这里，了不起",
        "dg_common_CanWarp#1": "若以吾之名许愿",
        "dg_common_CanWarp#2": "便即刻把你送到这大厅来",
        "dg_common_CanWarp_fst#0": "被封印的门：",
        "dg_common_CanWarp_fst#1": "吾之敌能否跨越",
        "dg_common_CanWarp_fst#2": "被封印的门：吾可从地下1层选择此处",
        "dg_common_CanWarp_fst#3": "被封印之门",
        "dg_common_CanWarp_fst#4": "被封印的门：若以吾之名许愿",
        "dg_common_CanWarp_fst#5": "便即刻把你送到这大厅来",
        "dg_common_CanWarp_fst#6": "被封印的门：再次踏入此处之时",
        "dg_common_CanWarp_fst#7": "当立于吾之名，以吾之名述说",
        "dg_common_Dead#0": "在迷宫深处力尽的人",
        "dg_common_Dead#1": "被不可思议的光包裹",
        "dg_common_Dead#2": "被带回原来的世界了！",
        "dg_common_Dead2#0": "在迷宫深处倒下的",
        "dg_common_Dead2#1": "身影",
        "dg_common_Dead2#2": "再也没有人看见过！",
        "dg_common_DoorChoose#0": "打开",
        "dg_common_DoorChoose#1": "算了",
        "dg_common_DoorMsg": "用它开门吗？",
        "dg_common_DoorMsgCannot": "没有它，门打不开",
        "dg_common_DownStair": "往下的楼梯",
        "dg_common_FullBagAbandon": "放弃了！",
        "dg_common_FullBagQuery#0": "得到了新的「」！",
        "dg_common_FullBagQuery#1": "可是，宝袋已经满了！",
        "dg_common_FullBagQueryChoose#0": "丢掉这个",
        "dg_common_FullBagQueryChoose#1": "丢掉别的东西",
        "dg_common_KeyBox": "上锁的宝箱",
        "dg_common_KeyDoor": "用钥匙开的门",
        "dg_common_MiniDoor": "小门",
        "dg_common_MiniDoor_Big": "以这种体型，钻这么小的门是不可能的！",
        "dg_common_Pit": "大坑",
        "dg_common_PitChoose#0": "跳下去看看",
        "dg_common_PitChoose#1": "算了",
        "dg_common_PitMsg": "感觉跳得下去",
        "dg_common_Raft": "木筏",
        "dg_common_RaftChoose#0": "乘坐",
        "dg_common_RaftChoose#1": "不要",
        "dg_common_RaftMsg": "坐上木筏？",
        "dg_common_RaftRideOff": "从木筏上下来",
        "dg_common_ReturnChoose#0": "累了",
        "dg_common_ReturnChoose#1": "还早",
        "dg_common_ReturnMsg": "差不多回去了？",
        "dg_common_ReturnStair": "回到地上的楼梯",
        "dg_common_SealDoor": "被封印的门",
        "dg_common_Timestop": "停止时间的开关",
        "dg_common_UpStair": "往上的楼梯",
        "dg_common_WarpCannot": "被封印的门紧紧关着",
        "dg_common_WarpMsg": "被封印的门：要许愿移动到何处",
        "dg_common_box_sentaku#0": "钥匙",
        "dg_common_box_sentaku#1": "普通的",
        "dg_common_box_sentaku#2": "毒",
        "dg_common_box_sentaku#3": "爆炸",
        "dg_common_box_sentaku#4": "奇怪的",
        "dg_common_box_trap#0": "毒",
        "dg_common_box_trap#1": "奇怪的",
        "dg_common_box_trap#2": "爆炸",
        "dg_common_box_trap#3": "你好拟态怪",
        "dg_common_china01#0": f"{CH}哎呀——！",
        "dg_common_china01#1": "你将军太少的啦！",
        "dg_common_china02#0": f"{CH}这可是危险状况的啦！",
        "dg_common_china02#1": "我来帮你！",
        "dg_common_china02#2": "将军一人10波奇利哟！",
        "dg_common_china03#0": f"{CH}你啊，将军人数不够",
        "dg_common_china03#1": "要全回复的话「波奇利」是必要的啦！",
        "dg_common_china04#0": f"{CH}不买会后悔哟！",
        "dg_common_china04#1": "这是真的呢！怎么办的啦？",
        "dg_common_china05#0": "买",
        "dg_common_china05#1": "不买",
        "dg_common_china06#0": f"{CH}霍伊！",
        "dg_common_china06#1": "客人，买得真好呢！",
        "dg_common_china07#0": f"{CH}还买的啦？",
        "dg_common_china07#1": "不买的啦？",
        "dg_common_china08#0": f"{CH}将军已经满满的啦！",
        "dg_common_china08#1": "再多带不了了呢！",
        "dg_common_china09#0": f"{CH}客人，恭维话先放下！",
        "dg_common_china09#1": "钱不够的啦！",
        "dg_common_china10#0": f"{CH}客人，绝对会后悔的哟！",
        "dg_common_china10#1": "怎样都好我可不管的啦！",
        "dg_common_china11#0": f"{CH}好像知道呢！",
        "dg_common_china11#1": "不停战斗，不停雇将军",
        "dg_common_china11#2": "再不停从我这儿买将军的啦！",
        "dg_common_homeless01#0": f"{HM}俺是住里面的流浪汉大叔！",
        "dg_common_homeless01#1": "就算这样也凭着相当的气势活着！",
        "dg_common_homeless01#2": "别同情俺啊！",
        "dg_common_homeless02#0": f"{HM}对了，你拿着的",
        "dg_common_homeless02#1": "「」能不能给我？",
        "dg_common_homeless02#2": "给的话俺把「」给你！",
        "dg_common_homeless02_2#0": "给",
        "dg_common_homeless02_2#1": "不给",
        "dg_common_homeless03#0": f"{HM}连能给俺的东西都没有？",
        "dg_common_homeless03#1": "别那么小气！",
        "dg_common_homeless03#2": "那样可成不了大人物啊！",
        "dg_common_homeless04#0": f"{HM}谢啦！",
        "dg_common_homeless04#1": "加进俺的收藏里！",
        "dg_common_homeless04_2#0": f"{HM}对了，再把「」",
        "dg_common_homeless04_2#1": "给我行不行？",
        "dg_common_homeless04_2#2": f"{HM}给的话刚才那个",
        "dg_common_homeless04_2#3": "换成「」！",
        "dg_common_homeless05#0": f"{HM}谢啦！",
        "dg_common_homeless05#1": "从俺的收藏里拿一个走！",
        "dg_common_homeless05_2#0": f"{HM}这样啊！嘛，谢啦！",
        "dg_common_homeless05_2#1": "你也从俺的收藏里拿一个走！",
        "dg_common_homeless06#0": "",
        "dg_common_homeless06#1": "入手了「」！",
        "dg_common_homeless07#0": f"{HM}哈？有什么事？",
        "dg_common_homeless07#1": "没事就赶紧消失！",
        "dg_common_homeless08#0": f"{HM}哦，又见面了！",
        "dg_common_homeless08#1": "还精神吗？",
        "dg_common_ice_info#0": "勇过于冰冷的冷笑话",
        "dg_common_ice_info#1": "把这一层冻住了。",
        "dg_common_lever": "门的杠杆",
        "dg_common_seal#0": "能走到这里，了不起",
        "dg_common_seal#1": "认可汝之力量",
        "dg_common_seal#2": "横跨宇宙的宏大迷宫",
        "dg_common_seal#3": "地下层的封印，就此为你解开！",
        "dg_common_seal2#0": "",
        "dg_common_seal2#1": "主迷宫「地下层」的封印解开了。",
        "dg_common_seal3#0": "这扇门似乎从某处遥远的地方",
        "dg_common_seal3#1": "被强大的力量封印着！",
        "dg_common_seal3#2": "打不开！",
        "dg_common_sel#0": "给",
        "dg_common_sel#1": "不给",
    }
    out.update(_warp_menus())
    return out
