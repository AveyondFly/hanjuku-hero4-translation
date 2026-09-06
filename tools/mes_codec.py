#!/usr/bin/env python3
"""Decode Hanjuku Hero 4 (SLPM-65839) message files.

On-disc / in-RAM .mes layout:
  u32 trie_root
  packed NUL-terminated strings + a byte trie of ASCII keys

Glyph bytes (KIWI):
  decoded = (byte * 189) & 0xFF
  if (decoded & 0xC3) == 0: control code
  elif (decoded & 3) != 0:  1-byte glyph 0..191
  else:                     2-byte glyph, engine adds +192 when in range
"""
from __future__ import annotations

import struct
from typing import Iterable

MUL = 189  # inverse of 149 mod 256
INV = 149  # (byte * 149) encodes t; (t * 189) recovers byte


def s16(x: int) -> int:
    x &= 0xFFFF
    return x - 0x10000 if x >= 0x8000 else x


def decode_font_codes(data: bytes, font_max: int = 12000, mul48: bool = False) -> list:
    """Return a list of int glyph ids and ('C', kind, extra) controls.

    mul48=True matches the patched EE decoder (mflo of a0*48).
    """
    out: list = []
    i = 0
    n = len(data)
    while i < n:
        b0 = data[i]
        if b0 == 0:
            break
        t = (b0 * MUL) & 0xFF
        if (t & 0xC3) == 0:
            kind = t >> 2
            i += 1
            extra = None
            if kind >= 8:
                if i >= n:
                    break
                b1 = data[i]
                i += 1
                extra = ((-b0) & 0xFF) if b1 == b0 else ((b1 - b0) & 0xFF)
            out.append(("C", kind, extra))
            continue
        low = t & 3
        if low != 0:
            out.append(s16((t >> 2) * 3 + (low - 1)))
            i += 1
        else:
            i += 1
            if i >= n:
                break
            b1 = data[i]
            i += 1
            v0 = ((-b1) & 0xFF) if b1 == b0 else ((b1 - b0) & 0xFF)
            a0 = (v0 - 1) & 0xFF
            add = (a0 * 48) if mul48 else a0
            code = s16(((t >> 2) + 0xFFF0 + add) & 0xFFFF)
            if 0 <= code < 12000:
                if code < font_max:
                    code = code + 192
            out.append(code)
    return out


def _enc_byte(t: int) -> int:
    return (t * INV) & 0xFF


def _enc_delta(b0: int, v0: int) -> int:
    """Second byte so decoder recovers v0 from (b1-b0) or (-b1) if equal.

    Encoded strings are NUL-terminated, so neither byte may be 0. When
    (b0+v0)&0xFF == 0 the additive path would emit NUL; that is exactly
    the decoder's b1==b0 path (v0 == -b0).
    """
    v0 &= 0xFF
    b1 = (b0 + v0) & 0xFF
    if b1 == 0 or b1 == b0:
        if ((-b0) & 0xFF) != v0:
            raise ValueError(f"cannot encode delta v0={v0} with b0={b0}")
        if b0 == 0:
            raise ValueError("delta encoding would emit NUL")
        return b0
    return b1


def encode_token(tok, mul48: bool = True) -> bytes:
    """Encode one decoded token (glyph int or ('C', kind, extra))."""
    if isinstance(tok, tuple) and tok[0] == "C":
        kind = int(tok[1])
        extra = tok[2]
        t = (kind << 2) & 0xFF
        b0 = _enc_byte(t)
        if kind >= 8:
            v0 = 0 if extra is None else (int(extra) & 0xFF)
            raw = bytes((b0, _enc_delta(b0, v0)))
        else:
            raw = bytes((b0,))
        if 0 in raw:
            raise ValueError(f"control {kind} encoded a NUL: {raw.hex()}")
        return raw
    g = int(tok)
    if 0 <= g < 192:
        hi, r = divmod(g, 3)
        t = (hi << 2) | (r + 1)
        b = _enc_byte(t)
        if b == 0:
            raise ValueError(f"glyph {g} encoded a NUL")
        return bytes((b,))
    idx = g - 192
    if idx < 0:
        raise ValueError(f"cannot encode glyph {g}")
    if not mul48:
        total = idx + 16
        # q in 16..63, a0 in 0..255, idx = q + a0 - 16
        if total > 63 + 255:
            raise ValueError(f"glyph {g} needs mul48 encoding")
        q = 16
        a0 = total - 16
        if a0 > 255:
            q = 63
            a0 = total - 63
        t = (q << 2) & 0xFF
        b0 = _enc_byte(t)
        raw = bytes((b0, _enc_delta(b0, (a0 + 1) & 0xFF)))
        if 0 in raw:
            raise ValueError(f"glyph {g} encoded a NUL: {raw.hex()}")
        return raw
    total = idx + 16
    a0, q = divmod(total, 48)
    if q < 16:
        a0 -= 1
        q += 48
    if not (16 <= q <= 63 and 0 <= a0 <= 255):
        raise ValueError(f"glyph {g} out of 2-byte range (q={q} a0={a0})")
    t = (q << 2) & 0xFF
    b0 = _enc_byte(t)
    raw = bytes((b0, _enc_delta(b0, (a0 + 1) & 0xFF)))
    if 0 in raw:
        raise ValueError(f"glyph {g} encoded a NUL: {raw.hex()}")
    return raw


def encode_tokens(tokens, mul48: bool = True) -> bytes:
    return b"".join(encode_token(t, mul48=mul48) for t in tokens)


def encode_text(text: str, cmap: dict[str, int], mul48: bool = True) -> bytes:
    toks = []
    for ch in text:
        if ch in "\n\r":
            continue
        g = cmap.get(ch)
        if g is None:
            continue
        toks.append(g)
    return encode_tokens(toks, mul48=mul48)


# Must match zh_csv.SKIP_CMAP_CHARS / build_kiwi_font extras skip.
SKIP_GLYPH = frozenset(" \t\n\r\u3000")

# PrintMes C8 extras that open the name plate; extra 189 closes it.
# Field/event mes uses 13; egg/battle mes uses 109 (often after color 203).
# Orig 482/254 were empty glue; 277/314 were JP 「. All four ids are
# real Chinese glyphs now (482=斗), so never copy or re-insert them.
_SPEAKER_OPEN = 13
_SPEAKER_OPENS = frozenset({13, 109, 203})
_SPEAKER_CLOSE = 189
_SKIP_AFTER_NAME = frozenset({482, 254, 277, 314})


class MissingGlyphs(ValueError):
    """zh contains characters that have no cmap id (would have been dropped)."""

    def __init__(self, chars: str):
        self.chars = chars
        super().__init__(f"not in cmap: {chars}")


def _is_ctrl(tok, kind: int, extra=None) -> bool:
    return (
        isinstance(tok, tuple)
        and tok[0] == "C"
        and tok[1] == kind
        and (extra is None or tok[2] == extra)
    )


def _zh_tokens(zh: str, cmap: dict[str, int]) -> list:
    """Map zh to glyph ids. Catalog newlines become PrintMes kind-1 breaks."""
    missing: list[str] = []
    seen_miss: set[str] = set()
    out: list = []
    for ch in zh:
        if ch == "\r":
            continue
        if ch == "\n":
            out.append(("C", 1, None))
            continue
        if ch in SKIP_GLYPH:
            continue
        g = cmap.get(ch)
        if g is None:
            if ch not in seen_miss:
                seen_miss.add(ch)
                missing.append(ch)
            continue
        out.append(g)
    if missing:
        raise MissingGlyphs("".join(missing))
    return out


def _split_speaker_zh(zh: str) -> tuple[str, str] | None:
    for sep in ("：", ":"):
        i = zh.find(sep)
        if i > 0:
            return zh[:i], zh[i + 1 :]
    return None


def _pop_trailing_ctrls(toks: list) -> tuple[list, list]:
    suffix: list = []
    while toks and isinstance(toks[-1], tuple):
        suffix.insert(0, toks.pop())
    return toks, suffix


def _speaker_open_index(toks: list) -> int | None:
    """Last C8 name-plate opener in the leading control run (before glyphs)."""
    i_open = None
    for i, t in enumerate(toks):
        if not isinstance(t, tuple):
            break
        if t[0] == "C" and t[1] == 8 and t[2] in _SPEAKER_OPENS:
            i_open = i
    return i_open


def encode_merged(orig: bytes, zh: str, cmap: dict[str, int], mul48: bool = True) -> bytes:
    """Replace orig glyphs with zh; keep PrintMes controls, including name plates.

    Dialogue strings are `C8:13|109` + name + `C8:189` + body. Egg/battle
    lines open with 109 (after color 203); field lines use 13. A previous
    merge that only looked for 13 flattened egg plates into one glyph run.
    Rebuild the closer. `名字：正文` fills the two sides; a C9 name insert
    in the name slot is left alone (the injected speaker).
    """
    toks = decode_font_codes(orig, mul48=False)
    i_open = _speaker_open_index(toks)
    if i_open is None:
        return encode_tokens(_merge_plain(toks, zh, cmap), mul48=mul48)
    i189 = next(
        (
            i
            for i, t in enumerate(toks)
            if i > i_open and _is_ctrl(t, 8, _SPEAKER_CLOSE)
        ),
        None,
    )
    if i189 is None:
        merged = _merge_speaker_recovered(toks, i_open, zh, cmap)
    else:
        merged = _merge_speaker(toks, i_open, i189, zh, cmap)
    return encode_tokens(merged, mul48=mul48)


def _merge_plain(toks: list, zh: str, cmap: dict[str, int]) -> list:
    prefix: list = []
    suffix: list = []
    seen_glyph = False
    for t in toks:
        if isinstance(t, tuple):
            if not seen_glyph:
                prefix.append(t)
            else:
                suffix.append(t)
        else:
            seen_glyph = True
    return list(prefix) + _zh_tokens(zh, cmap) + list(suffix)


def _merge_speaker(toks: list, i13: int, i189: int, zh: str, cmap: dict[str, int]) -> list:
    head = toks[: i13 + 1]
    orig_name = toks[i13 + 1 : i189]
    rest = list(toks[i189 + 1 :])
    rest, suffix = _pop_trailing_ctrls(rest)
    bridge: list = []
    while rest and (
        isinstance(rest[0], tuple) or rest[0] in _SKIP_AFTER_NAME
    ):
        t = rest.pop(0)
        if isinstance(t, int):
            continue
        bridge.append(t)
    name_has_ctrl = any(isinstance(t, tuple) for t in orig_name)
    split = _split_speaker_zh(zh)
    if name_has_ctrl:
        name_toks = list(orig_name)
        body_toks = _zh_tokens(zh, cmap)
    elif split:
        name_toks = _zh_tokens(split[0], cmap)
        body_toks = _zh_tokens(split[1], cmap)
    else:
        name_toks = list(orig_name)
        body_toks = _zh_tokens(zh, cmap)
    return (
        list(head)
        + name_toks
        + [("C", 8, _SPEAKER_CLOSE)]
        + bridge
        + body_toks
        + suffix
    )


def _merge_speaker_recovered(toks: list, i13: int, zh: str, cmap: dict[str, int]) -> list:
    """ISO already lost C8:189; rebuild it from `名字：正文`."""
    head = toks[: i13 + 1]
    rest = list(toks[i13 + 1 :])
    rest, suffix = _pop_trailing_ctrls(rest)
    split = _split_speaker_zh(zh)
    if split:
        name_toks = _zh_tokens(split[0], cmap)
        body_toks = _zh_tokens(split[1], cmap)
    else:
        name_toks = []
        body_toks = _zh_tokens(zh, cmap)
    return (
        list(head)
        + name_toks
        + [("C", 8, _SPEAKER_CLOSE)]
        + body_toks
        + suffix
    )


def pack_trie(entries: list[tuple[bytes, list[bytes]]]) -> bytes:
    """Build a .mes blob from (key, strings) rows.

    Duplicate keys exist in the original files (two NUL leaves under the
    same prefix). Keep them as duplicate child bytes so lookup still sees
    both leaves.
    """

    class Node:
        __slots__ = ("child", "leaf")

        def __init__(self) -> None:
            self.child: list[tuple[int, Node]] = []
            self.leaf: list[bytes] | None = None

    root = Node()
    for key, strs in entries:
        k = key.rstrip(b"\x00") + b"\x00"
        n = root
        for i, b in enumerate(k):
            last = i == len(k) - 1
            if last:
                leaf = Node()
                leaf.leaf = strs
                n.child.append((b, leaf))
                break
            nxt = None
            for bb, ch in n.child:
                if bb == b and ch.leaf is None:
                    nxt = ch
                    break
            if nxt is None:
                nxt = Node()
                n.child.append((b, nxt))
            n = nxt

    data = bytearray(4)

    def emit_strings(strs: list[bytes]) -> int:
        off = len(data)
        data.extend(struct.pack("<I", len(strs)))
        for s in strs:
            data.extend(s)
            data.append(0)
        return off

    def emit_node(node: Node) -> int:
        if node.leaf is not None and not node.child:
            return emit_strings(node.leaf) | 0x80000000
        items = sorted(node.child, key=lambda x: x[0])
        child_raw = []
        for b, ch in items:
            if ch.leaf is not None and not ch.child:
                child_raw.append((b, emit_strings(ch.leaf) | 0x80000000))
            else:
                child_raw.append((b, emit_node(ch)))
        n = len(child_raw)
        keys = bytes(b for b, _ in child_raw)
        off = len(data)
        data.extend(struct.pack("<I", n))
        data.extend(keys)
        table_off = (off + 4 + n + 3) & ~3
        data.extend(b"\x00" * (table_off - len(data)))
        for _, ptr in child_raw:
            data.extend(struct.pack("<I", ptr & 0xFFFFFFFF))
        return off

    root_off = emit_node(root)
    struct.pack_into("<I", data, 0, root_off)
    return bytes(data)



# Hiragana 0-89, verified against:
#   はじめから, つづきから, オプション, こうげき, ぼうぎょ, じんけい, せいしん
HIRA = [""] * 90
HIRA[0:5] = list("あいうえお")
HIRA[5:10] = list("かきくけこ")
HIRA[10:15] = list("さしすせそ")
HIRA[15:20] = list("たちつてと")
HIRA[20:25] = list("なにぬねの")
HIRA[25:30] = list("はひふへほ")
HIRA[30:35] = list("まみむめも")
HIRA[35] = "や"
HIRA[37] = "ゆ"
HIRA[39] = "よ"
HIRA[40:45] = list("らりるれろ")
HIRA[45] = "わ"
HIRA[47] = "を"
HIRA[49] = "ん"
HIRA[50] = "ぁ"
HIRA[51] = "ぃ"
HIRA[52] = "ぅ"
HIRA[53] = "ぇ"
HIRA[54] = "ぉ"
HIRA[55] = "ゃ"
HIRA[57] = "ゅ"
HIRA[59] = "ょ"
HIRA[60:65] = list("がぎぐげご")
HIRA[65:70] = list("ざじずぜぞ")
HIRA[70:75] = list("だぢづでど")
HIRA[75:80] = list("ばびぶべぼ")
HIRA[80:85] = list("ぱぴぷぺぽ")
HIRA[85] = "ー"  # 1-byte chōon; ん is 49
HIRA[86] = "っ"
HIRA[87] = "っ"  # うむっ / エッグ (ッ after katakana)

# 2-byte / high 1-byte codes. Filled from Japanese sentence context
# (kana conjugation, unique compounds). Atlas index is not a cmap:
# different KIWI styles store different bitmaps at the same code.
#
# A few codes are reused in more than one word (e.g. 469 in 英雄 and
# 込む). Grammar (〜んで / 〜んだ) is preferred over proper nouns.
#
# Name-entry A–Z overlay (same slots as kanji; catalog keeps the Japanese
# reading except N/O, which had no kanji mapping). Row 2 of sysmes_alphabet:
#   A知 B死 C体 D複 E少 F教 G早 H能 I惑 J分 K守 L小 M中
#   N=488 O=305 P力 Q激 R使 S大 T喜 U勢 V誰 W捨 X装 Y備 Z威
# Readable as Latin in-game: DUALSHOCK2, NODATA, BROKEN DATA, HOT, OK,
# DEFCON, ATOM, LOM, HN190921U, UP/DOWN/LEFT/RIGHT.
SPECIAL = {
    # --- controls / empty slots (not spoken) ---
    192: "",
    222: "人",  # 1人から3人 / 人それぞれ; bitmap empty in RAM fonts
    224: "",  # infix in はやくして
    254: "",  # empty; speaker-tag glue 惑□大戦
    255: "",  # planet-name prefix (color/icon)
    299: "",  # dialogue wait / page break
    412: "",
    482: "",  # line-prefix marker
    # --- digits / ascii (bank0 180-190, verified in atlas) ---
    180: "1",
    181: "2",
    182: "3",
    183: "4",
    184: "5",
    185: "6",
    186: "7",
    187: "8",
    188: "9",
    189: "0",
    190: "@",
    # --- punctuation ---
    227: "、",
    229: "。",
    264: "ー",
    277: "「",
    278: "」",
    279: "：",
    286: "・",
    287: "・",
    288: "…",
    300: "！",
    302: "？",
    331: "。",
    444: "・",  # キリー・フッダー / カトリ・デ・オマール
    257: "？",
    # --- kanji, high-confidence compounds / conjugations ---
    195: "星",  # 惑星
    328: "星",  # ある星に / 星アルマムーン
    347: "気",
    379: "惑",
    372: "変",
    326: "読",
    443: "戦",  # 戦い / 戦う / 戦え
    281: "攻",  # 攻撃 / 攻め込んだ / 攻めこめ
    319: "撃",  # 攻撃 130x, 出撃
    329: "出",  # 出現 / 出る / 出撃 / 生み出す
    321: "現",  # 出現した
    242: "移",  # 移動
    315: "動",  # 移動 / 動かせます
    209: "部",  # 部隊 484x
    282: "隊",  # 部隊; also 隊に攻め込まれた
    374: "楽",  # 楽しみ
    423: "待",  # 待っておるぞ; also 準備 (準) in some lines
    339: "生",  # 生き / 生まれ / 生み出す
    469: "雄",  # 半熟英雄4; 攻め込んだ も同一号（込と衝突）
    250: "半",  # 半熟英雄
    323: "熟",
    396: "英",  # 英雄; also 包まれた / お茶漬け in other lines
    241: "敵",  # 敵星があるところには移動できませぬ
    306: "能",  # 能力 221x
    341: "力",  # 能力 / 力が
    304: "大",  # 大・中・小
    415: "中",
    342: "小",  # 小サイズ; 果たして は別解釈の衝突
    413: "装",  # 装備していると
    230: "備",  # 装備; お願い は別解釈の衝突
    310: "",  # stat/name highlight before せいしん/こうげき/きりふだ
    383: "力",  # せいしん力 / こうげき力がアップ
    243: "挑",  # 戦いに挑んだ
    392: "繰",  # 繰り出す
    317: "",  # icon before メインメニュー
    244: "",  # icon before 半熟英雄にもどる
    314: "「",  # 「半熟英雄4」のセーブデータ
    387: "」",
    231: "使",  # 使うことができるからの
    335: "進",  # 進める
    420: "所",  # 場所（装所 と出る行あり。装備の装と衝突）
    258: "壊",  # セーブデータが壊れています
    262: "選",  # 選ぶ / 選択
    239: "択",  # 選択して
    427: "○",  # ○ボタンで選択
    343: "少",  # 少しだけ
    467: "逃",  # 逃げる
    405: "入",  # 入れ替え / 入口
    428: "心",  # 人心
    433: "思",  # 思っている
    398: "他",  # 他の星や
    208: "明",  # 明らかに眠った
    265: "見",  # 見られない / 見せたる
    324: "踊",  # ダンスを踊って
    216: "反",  # 反撃ですぞ
    448: "持",  # 持つ / 持っていく
    380: "死",  # 死んでしまった
    447: "姿",  # 姿をあらわした
    292: "降",  # 降臨する
    368: "臨",
    394: "改",  # 改造
    352: "造",
    366: "回",  # 回復
    439: "復",
    318: "集",
    475: "合",  # 集合
    353: "殿",  # セバスチャン殿
    468: "初",  # 初めての戦い
    238: "始",  # 始まります
    316: "使",  # 使う
    441: "用",  # 使用
    390: "与",  # ダメージを与える
    430: "感",  # 感じる
    283: "悩",  # 悩む
    345: "眠",  # 眠りたいなら眠れば; save-slot term_b#26 is 8bpp clock 70, zh ⌚
    384: "強",  # 強くなる
    256: "弱",  # 弱らなくなる
    # --- batch: UI compounds / okurigana (2026-09-04) ---
    175: "ー",  # オーァリウム / katakana keyboard
    201: "友",  # 友だち / 友情出演
    214: "力",  # 入力します / ○入力（能力の力 341 と別号）
    228: "）",  # メモリーカード（PS2） / 1人につき1ポッキリ）
    245: "配",  # 心配 / 配えますか（ユニットの中配＝中央と衝突）
    248: "地",  # 本拠地（装=拠と衝突し 本装地 と出る行あり）
    252: "号",  # 英数字・記号
    257: "決",  # 決めてください / 決めたら / 決まって（旧？は 302）
    260: "了",  # 終了します（有利の利と衝突）
    267: "誰",  # 誰かひとり（現在の在と衝突）
    274: "情",  # 友情
    280: "将",  # ヒマな将軍
    285: "上",  # 少しだけ上がる / これ以上
    289: "好",  # 好きな人 / 好み（攻略・全滅の略/滅と衝突）
    291: "食",  # 食らう
    293: "軍",  # 将軍
    294: "定",  # 決定
    297: "全",  # 全滅（好=滅と衝突）/ 全員
    298: "編",  # 編成（弱=成と衝突し 編弱 と出る）
    301: "数",  # 英数字 / 部隊数 / 持っている数
    325: "終",  # 終わった / 終わり / 終了
    337: "喚",  # 召喚（ー=召と衝突し ー喚する）
    346: "気",  # 眠気（347 も気）
    355: "長",  # 隊長（name-entry 繰部隊長）
    362: "本",  # 本拠地 / 本当
    364: "呼",  # お呼びいたしましょう / 呼ばれる（俺たちと衝突）
    377: "喜",  # 喜びのカタマリ
    381: "道",  # 現れた道をたどり
    393: "造",  # {393}改=改造（352 も造）
    401: "字",  # 英数字
    403: "開",  # 開始 / とびらを開く（戻・貢・帰と衝突）
    411: "（",  # メモリーカード（PS2）
    416: "教",  # を教える（山のごとし・FFシリーズと衝突）
    424: "中",  # セーブ中 / たまごの中に（415 も中）
    435: "当",  # 本当に
    445: "一",  # 一撃 / 一緒 / 一覧（最強の最と衝突）
    452: "分",  # 分けられます / 半分
    453: "体",  # 1体もいません
    454: "体",  # 一体となり（453 も体。地球ちゃんは地体）
    455: "敗",  # 失敗しました（失われたハートは 敗れた と出る）
    466: "土",  # お土産 / 土に入れた（袋と衝突しうる）
    # --- batch 2 ---
    220: "発",  # 開発スタッフ / 発見する / 発生
    235: "間",  # 人間
    237: "打",  # 連打
    240: "大",  # 大きさ / 全部（304 も大）
    249: "連",  # 連れてこられた / 連打
    251: "帰",  # もう帰ってもいい / 帰ろう
    268: "活",  # 復活（反=復と衝突し 反活 と出る行あり）
    272: "新",  # 新しいエッグモンスター
    284: "撤",  # 撤収
    296: "負",  # 負けセリフ / 負ける
    307: "知",  # 知る人ぞ知る / 知っていたら
    309: "解",  # 解雇しないで（将=雇と衝突し 解将）
    311: "金",  # 金がほしい
    327: "日",  # つね日ごろ（長いと衝突）
    332: "収",  # 撤収（忘れると衝突し 収れる）
    359: "世",  # とある世界では（図鑑の鑑と衝突）
    361: "役",  # 役に立ちます（減少の減と衝突）
    373: "／",  # 1／4 / ステレオ／モノラル
    385: "立",  # 役に立ちます / 立ち上がる / 立ち読み
    389: "空",  # 空中でできた（図鑑話者名・星間と衝突）
    432: "界",  # 世界
    434: "占",  # 占領した（人数表示の表と衝突）
    436: "状",  # 状況（？=況と衝突）
    438: "消",  # 消えてしまう
    462: "箱",  # カギのかかった箱
    463: "占",  # 本拠地を占将せ（領と衝突）
    # --- batch 3 ---
    233: "早",  # まだ早すぎます
    263: "近",  # 近くみるなよ / 近く見ないで
    266: "欲",  # 欲しい（お姉ちゃんと衝突）
    269: "守",  # 守りつつ / 守りとおせ
    271: "小",  # 小さくなる（342 も小）
    303: "威",  # 威力部がアップ
    313: "事",  # 大事に悩む
    322: "闘",  # 戦闘に長けてる
    336: "【",  # 月次メニュー見出し
    340: "捨",  # 捨てる / 捨てて
    354: "番",  # 一番（全員の員と衝突）
    358: "映",  # 映像を見ますか（繰=像と衝突）
    360: "不",  # 不思議な（半=議と衝突）
    363: "怪",  # 怪しげな
    367: "落",  # 星を落とせ
    391: "団",  # 集団 / 団になった部隊
    399: "軍",  # 将軍（293 も軍。使用の用と衝突）
    404: "効",  # 効果（小=果と衝突し 効小）
    409: "】",  # 月次メニュー見出し
    414: "激",  # 激しく体を動かしたくて
    418: "時",  # 時間がありません
    421: "以",  # それ以外（友=外と衝突）
    431: "討",  # 討ち
    460: "合",  # 気合（475 も合）
    # --- batch 4 ---
    215: "休",  # 休日 / 休もう
    273: "外",  # 以外
    276: "足",  # ポッキリが足りません
    295: "陣",  # 陣形（臨=形と衝突）
    320: "怖",  # ホントは怖いんだ
    330: "夢",  # 夢みたい / 小さいころの夢
    382: "形",  # 姿形
    388: "周",  # 周回
    395: "優",  # 優しくても
    410: "修",  # 修復をして（危ないと衝突）
    440: "投",  # ボムを投げて / ポッキリを投げる
    442: "置",  # 配置地（入ったらと衝突）
    446: "場",  # 場・入に出入り（戦場。界=戦と衝突し 界場）
    # --- batch 5 ---
    270: "複",  # 複数装備（アナログ等と衝突）
    290: "核",  # 核ミサイル
    308: "赤",  # 赤ちゃん / 赤字
    365: "書",  # 上書きしてもよろしい（続ける・着ぐるみと衝突）
    375: "白",  # 白兵戦
    426: "可",  # 不可能（全惑星の全と衝突）
    437: "勇",  # 勇気（曲と衝突）
    # --- batch 6 ---
    217: "美",  # 美しい
    221: "生",  # 生活（339 も生）
    223: "失",  # 失敗しました（455=敗）
    234: "由",  # 自由（417=自。惑由に動かせます は 惑=自 衝突）
    246: "来",  # ところに来れば
    253: "況",  # 戦況を表示
    259: "容",  # 空き容量が不足（間=量と衝突）
    275: "客",  # お客さん（転移と衝突）
    333: "完",  # 完全回復
    338: "施",  # コーティングが施されている
    344: "十",  # 十分おります（正しくと衝突）
    348: "超",  # 英雄をも超えて（友達の達と衝突）
    351: "任",  # 任せてくれよ
    357: "飛",  # 飛ばす / 飛び出した / すっ飛ばして
    369: "頼",  # よろしくお願いします（願います）
    370: "操",  # 操作して（外=作と衝突）
    386: "静",  # 静かなところ
    397: "魔",  # 魔法 / 魔星（ボス星と衝突）
    402: "費",  # 費用がかかります（誰=用と衝突）
    408: "報",  # 情報です
    417: "自",  # 自由
    419: "潜",  # 潜入
    429: "飲",  # 飲む / 飲んで / 飲まない
    449: "連",  # 英雄連合（249 も連）
    450: "勢",  # 勢ったいきおいで
    456: "今",  # 今回
    457: "商",  # 商人（フッダー商人）
    459: "揺",  # 画面の揺れ（再開と衝突し 揺開）
    461: "捕",  # 捕らえ / 捕らえた
    474: "嫌",  # 嫌気がさし
    476: "臭",  # 臭いがする
    481: "末",  # 終末 / 結末
    # --- batch 7 ---
    207: "",  # planet-command icon prefix
    210: "叩",  # 叩き込まれ / 叩き起こし
    236: "様",  # 殿様
    247: "親",  # 親しみ
    312: "先",  # 先しといて
    334: "起",  # 起こらなかった / 起こして / 起動中
    350: "協",  # ご協力ありがとう
    356: "聖",  # 聖剣伝説2/3からの（初=剣,収=伝,使=説 と衝突）
    376: "抜",  # 抜き差ししないで / 抜かれました
    378: "姫",  # お姫さま（有効と衝突）
    406: "識",  # 知識
    407: "属",  # 所属します
    422: "欲",  # 食欲（266 も欲）
    489: "作",  # 新作のネタ
    # --- batch 8 ---
    202: "葉",  # ひみつの言葉 / 早口言葉 / 言葉づかい（始=言と衝突）
    232: "準",  # 準備して出撃（備=230。守準能=守備）
    261: "疲",  # お疲れさま / 疲れてる
    400: "夜",  # 夜に現る
    371: "測",  # テンションを測っております
    # --- batch 9: last unmapped + Latin N/O (name-entry row 2) ---
    203: "暇",  # 余暇があったから（所=余と衝突）
    305: "O",  # alphabet N-O-P…; DUALSHOCK2 / NODATA / HOT / OK / ATOM / DEFCON
    349: "妹",  # カトリイネの妹 / キャノン姉妹 / 人質（踏・様と衝突）
    425: "繰",  # 繰り返す（392も繰。炎の魔人・火炎ビンと衝突）
    470: "宙",  # 宇宙人軍（逃亡・海と衝突）
    488: "N",  # alphabet; NODATA / HN190921U / DOWN（並べると衝突）
}


def hira_to_kata(ch: str) -> str:
    if not ch:
        return ch
    o = ord(ch)
    if 0x3041 <= o <= 0x3096:
        return chr(o + 0x60)
    return ch


def glyph_to_char(code) -> str:
    if isinstance(code, tuple):
        return ""
    if not isinstance(code, int):
        return ""
    if 0 <= code < 90 and HIRA[code]:
        return HIRA[code]
    if 90 <= code < 180:
        h = code - 90
        if 0 <= h < 90 and HIRA[h]:
            return hira_to_kata(HIRA[h])
    if code in SPECIAL:
        return SPECIAL[code]
    # ASCII-ish: some UI uses 1-byte codes 175+; leave as placeholder
    return f"{{{code}}}"


def codes_to_text(codes: Iterable) -> str:
    s = "".join(glyph_to_char(c) for c in codes)
    out = []
    for i, ch in enumerate(s):
        if ch == "っ" and i > 0 and "\u30a0" <= s[i - 1] <= "\u30ff":
            out.append("ッ")
        else:
            out.append(ch)
    return "".join(out)


def decode_string(raw: bytes) -> str:
    return codes_to_text(decode_font_codes(raw))


def walk_trie(data: bytes) -> list[tuple[bytes, list[bytes]]]:
    size = len(data)
    if size < 8:
        return []
    root = struct.unpack_from("<I", data, 0)[0]
    if root >= size:
        return []
    results: list[tuple[bytes, list[bytes]]] = []
    stack = [(root, b"")]
    seen: set[int] = set()
    while stack:
        node, prefix = stack.pop()
        if node in seen or node + 4 > size:
            continue
        seen.add(node)
        n = struct.unpack_from("<I", data, node)[0]
        if n <= 0 or n > 256:
            continue
        keys_off = node + 4
        if keys_off + n > size:
            continue
        keys = data[keys_off : keys_off + n]
        table_off = (keys_off + n + 3) & ~3
        if table_off + 4 * n > size:
            continue
        for i, ch in enumerate(keys):
            child = struct.unpack_from("<i", data, table_off + 4 * i)[0]
            new_prefix = prefix + bytes([ch])
            if child >= 0:
                if child < size:
                    stack.append((child, new_prefix))
            else:
                off = child & 0x7FFFFFFF
                if off + 4 > size:
                    continue
                count = struct.unpack_from("<I", data, off)[0]
                if not (0 <= count <= 8000):
                    continue
                p = off + 4
                strs: list[bytes] = []
                ok = True
                for _ in range(count):
                    z = data.find(b"\x00", p, size)
                    if z < 0:
                        ok = False
                        break
                    strs.append(data[p:z])
                    p = z + 1
                if ok:
                    results.append((new_prefix.rstrip(b"\x00"), strs))
    return results


def looks_like_mes(data: bytes) -> bool:
    if len(data) < 16:
        return False
    root = struct.unpack_from("<I", data, 0)[0]
    if root < 4 or root + 8 > len(data):
        return False
    n = struct.unpack_from("<I", data, root)[0]
    if not (1 <= n <= 64):
        return False
    keys = data[root + 4 : root + 4 + n]
    if not keys:
        return False
    # keys are mostly printable / SJIS
    good = sum(1 for b in keys if 0x20 <= b < 0x7F or b >= 0x80)
    return good >= max(1, n - 2)
