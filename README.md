# 半熟英雄4 中文化

PS2《半熟英雄4 ～7人の半熟英雄～》（SLPM-65839）文案 / 字库汉化。光盘 `半熟英雄4-7人的半熟英雄.iso` 不入库。

**译文只在 CSV 里。** 对照改 `extracted/translation_catalog.csv` 的 jp / zh 列；不要往 Python 里硬编码句子。旧的 `tools/zh_story_*.py`、`zh_pack.py` 等已经删掉，灌盘脚本也不再读它们。

格式细节见 `extracted/RESOURCE_MAP.txt`，专名见 `extracted/GLOSSARY.txt`。

## 硬约束

- **日文汉字不能当中文用。** 原版 bank1 同一字形号会撞字（雄/四、始/言 等）。汉化必须重建 cmap，按中文重编码 mes。
- 空 jp 保持空 zh。假名输入表、图鉴假名索引、合言葉保持原文（`kind=keep`，灌盘时不按中文重编码）。
- 译文里不要残留日文汉字或假名（上一条除外）。
- 第一版不砍低频字：bank0 仍是原版 192 个假名/数字，bank1 约 2760 个中文/标点/拉丁。

## 光盘怎么组织

ISO9660 里几乎只有启动 ELF（`SLPM_658.39`，LBA **931018**）。游戏资源在无名扇区，由 ELF 哈希表索引：

| | |
|---|---|
| 表 VA | `0x432C48`，19967 槽 × 12 字节 |
| 槽字段 | LBA、打包大小、解压大小（0 = 未压缩） |
| 字库包 | 槽 **49**，magic `0x19283746` + LZSS |
| mes | 约 43 个文案包，索引在 `extracted/mes_file_index.csv` |

变大的文件追加到 ISO 末尾，并改哈希表（含同 LBA 别名槽）。ELF 写回原 LBA。

## 流水线

```
ISO + ELF 哈希表
    → extract_mes.py          抽出 mes，生成 / 保留 catalog 的 jp
    → 编辑 CSV 的 zh 列       对照 jp
    → apply_zh.py             填 kind，写出 keep / alphabet 分表
    → build_kiwi_font.py      按 zh 字符集出 cmap + KIWI 点阵
    → patch_iso.py            读 CSV 的 zh，改解码器、灌字库、重编码 mes
```

路径相对仓库根（由脚本自己的位置推出来），不依赖当前工作目录。系统字体仍用发行版路径（Noto Sans CJK）。

### 1. 抽出文案

需要本机 ISO，以及一次 PCSX2 内存转储 `extracted/ram/eeMemory.bin`（导出字库、核对 sysmes）。

```
python3 tools/extract_mes.py
```

得到：

- `extracted/mes/*.bin` — 光盘 / RAM 里的 mes
- `extracted/text/` — 解码预览
- `extracted/translation_catalog.csv` — `id,jp,zh,notes,kind`（约 24468 条；已有 zh 会保留）

`id` 是 mes 的 ASCII key；同一 key 多行时为 `key#0`、`key#1`…。解码规则在 `tools/mes_codec.py`：字节 ×189 mod 256 还原；1 字节码 0–191 为假名 bank0；2 字节码在范围内再 +192 进 bank1。

改 `SPECIAL` 撞字表后，只重解文本、不改 ISO：

```
python3 tools/redecode_mes.py
```

### 2. 写中文（CSV 对照）

打开 CSV，jp / zh 并排改。`tools/apply_zh.py`、`tools/patch_iso.py`、`tools/build_kiwi_font.py` 都从这些表读中文，仓库里没有按文件拆开的译文 `.py`。

| 文件 | 列 | 用途 |
|---|---|---|
| `extracted/translation_catalog.csv` | id, jp, zh, notes, kind | 全部 mes。对照改这一张即可 |
| `extracted/zh_keep.csv` | 同上 | 假名输入表、图鉴假名索引、合言葉。zh 必须等于 jp，灌盘时不按中文重编码 |
| `extracted/zh_alphabet.csv` | 同上 | 姓名输入格。jp 是和汉字共槽的旧字形（知/死/体…），zh 是 A–Z 和数字。字槽特殊，所以单独一张方便核对 |
| `extracted/zh_cmap.csv` | char, hex, glyph | 字库映射，不是文案 |

`kind`：`text` 译文 / `keep` 保日文 / `alphabet` 姓名格 / `copy` 标点标记（zh 拷 jp） / `empty` 空串。

空 jp 保持空 zh。合言葉、假名表不要译成中文。专名跟 `GLOSSARY.txt`。

改完姓名格可以只改 `zh_alphabet.csv`，再跑：

```
python3 tools/apply_zh.py
```

它会把 alphabet 分表写回总表，给每行补 kind，并刷新两张分表。`patch_iso.py` / `build_kiwi_font.py` 都从这些 CSV 读中文。

### 3. 建中文字库

依赖 Noto Sans CJK（Bold，否则 Regular）和 Pillow。从 RAM 里原版 KIWI 抄 bank0 点阵，bank1 按 catalog 里出现过的字栅格化：

```
python3 tools/build_kiwi_font.py
```

写出：

- `extracted/zh_cmap.csv` — 字符 → glyph id
- `extracted/font/zh/kiwi_16x16.bin` / `kiwi_12x12.bin`
- `extracted/zh_char_freq.csv` / `zh_char_rare.csv` — 字频，第一版不用来删字

盘上 KIWI 是 **64 字节头 + 调色板 + 点阵 + 度量**。builder 在头后插了 20 字节 RAM 指针表，灌盘时要丢掉。

运行时 6 套字库里，汉化替换的是 style 1（主 16×16）和两套 12×12。其余（中等 16×16、8bpp 彩字等）仍是日文。

### 4. 灌盘

```
python3 tools/patch_iso.py
```

做三件事：

1. **ELF 2 字节解码器**（VA `0x2DBDB8`，72 字节）  
   原版有死的 `mult a0,48`，加的却是 `a0`（delta−1）不是 LO，所以原盘 2 字节码实际是 `code = q + a0 − 16`。中文 bank1 远超这个范围，必须变成真的 ×48：

   `code = q + 48·a0 − 16`（再按范围 +192）

   补丁：nop 掉前面的 `mult v0,35`，用移位做 ×48（`sll 5` + `sll 4` + `addu`）。不要用紧挨着的 `mflo`（PCSX2 上 LO 不对，字形会全变成「あ」= id 0）；也不要把 `addu` 的 rd 写成 `$s0`（那是字符串指针，结果只显示第一个字）。

2. **字库包**（槽 49）  
   解开 F7+LZSS，换 idx0 / idx2 / idx3，再压缩写回；放不下就追加扇区并改哈希。

3. **mes**  
   有 zh 的条目：保留原串首尾控制码，中间按 cmap 重编码（`mul48=True`）。  
   无 zh、或 KEEP_RAW（`sysmes_hiragana` / `sysmes_katakana` / `sysmes_dic_index_keyword` / `menu_secret_egg_word`）：只把旧 2 字节码转成新公式，字形号不变。  
   编码不能产出 NUL（mes 以 0 结尾）；`pack_trie` 必须保留原文件里的重复叶子。

同时写 `extracted/SLPM_658.39` 和 ISO 里那份 ELF。ELF 一改，PCSX2 存档目录按 CRC 分，旧档对不上。

## 改译文之后怎么重灌

1. 改 `extracted/translation_catalog.csv` 的 zh 列（或 `zh_alphabet.csv`）
2. `python3 tools/apply_zh.py`
3. 若出现了 cmap 里没有的新字：`python3 tools/build_kiwi_font.py`
4. `python3 tools/patch_iso.py`
5. 用本机 ISO 开 PCSX2

## 故意没改的

| 内容 | 原因 |
|---|---|
| 大标题「半熟英雄４」 | TIM2 图，不是 mes |
| 宙斯等角色显示名 | 在 EGG 资源里，不在 mes |
| 合言葉 / 假名输入表 | 对照攻略、输入法 |
| NODATA / DUALSHOCK2 等 | 拉丁和日文汉字共槽，姓名输入另处理 |
| 音频 | 没动；没声是主机 HDMI 输出，不是盘 |

## 仓库里有什么

| 路径 | 作用 |
|---|---|
| `extracted/translation_catalog.csv` | 原文 + 汉化总表 |
| `extracted/zh_keep.csv` | 必须保留日文的对照表 |
| `extracted/zh_alphabet.csv` | 姓名输入格（字形共槽） |
| `extracted/GLOSSARY.txt` | 专名 |
| `extracted/zh_cmap.csv` | 字形映射 |
| `extracted/mes_file_index.csv` | mes LBA / 槽 |
| `tools/zh_csv.py` | 读上述 CSV（不是译文本身） |
| `tools/apply_zh.py` | 规范化 catalog / 分表 |
| `tools/extract_mes.py` | 从 ISO 抽出 mes，保留已有 zh |
| `tools/redecode_mes.py` | 改 SPECIAL 后重解 jp，保留 zh |
| `tools/mes_codec.py` | 编解码、NUL 回避、trie |
| `tools/lzss.py` | 游戏用 LZSS 解/压 |
| `tools/patch_iso.py` | 解码器 + 字库 + mes 灌盘 |
| `tools/build_kiwi_font.py` | 中文 KIWI |

ISO、ELF 转储、RAM、点阵 bin 都在 `.gitignore` 里。
