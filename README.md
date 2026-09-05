# 半熟英雄4 中文化

PS2《半熟英雄4 ～7人の半熟英雄～》（SLPM-65839）文案 / 字库汉化。光盘 `半熟英雄4-7人的半熟英雄.iso` 不入库。

**译文只在 CSV 里。** 对照改 `extracted/catalog/` 下按章／归属拆开的分表（jp / zh 列）；不要往 Python 里硬编码句子。旧的 `tools/zh_story_*.py`、`zh_pack.py` 等已经删掉，灌盘脚本也不再读它们。分表说明见 `extracted/catalog/INDEX.txt`。

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
    → extract_mes.py          抽出 mes，写入 extracted/catalog/ 分表（保留 zh）
    → 编辑对应分表的 zh 列     或 catalog_query.py set
    → rebuild.py              一键：规范化 + 缺字补字库 + 灌 mes/字库/将军表
```

分步脚本仍可单独跑（`apply_zh.py` / `build_kiwi_font.py` / `patch_iso.py` / `patch_generals.py`）。改完译文请用总入口，避免漏建字库时把缺字丢掉。

路径相对仓库根（由脚本自己的位置推出来），不依赖当前工作目录。系统字体仍用发行版路径（Noto Sans CJK）。

### 1. 抽出文案

需要本机 ISO，以及一次 PCSX2 内存转储 `extracted/ram/eeMemory.bin`（导出字库、核对 sysmes）。

```
python3 tools/extract_mes.py
```

得到：

- `extracted/mes/*.bin` — 光盘 / RAM 里的 mes
- `extracted/text/` — 解码预览
- `extracted/catalog/` — `id,jp,zh,notes,kind`，按章／归属拆开（已有 zh 会保留；将军名也在这里）

`id` 是 mes 的 ASCII key；同一 key 多行时为 `key#0`、`key#1`…。解码规则在 `tools/mes_codec.py`：字节 ×189 mod 256 还原；1 字节码 0–191 为假名 bank0；2 字节码在范围内再 +192 进 bank1。

改 `SPECIAL` 撞字表后，只重解文本、不改 ISO：

```
python3 tools/redecode_mes.py
```

### 2. 写中文（CSV 对照）

译文在 `extracted/catalog/`，按章和归属拆开，没有总表。行数和说明以 `extracted/catalog/INDEX.txt` 为准。灌盘脚本读整个目录。

| 分表 | 内容 |
|---|---|
| `ch01_sun.csv` | 第一章 阿尔玛之月（日曜 `ev_sun` / `f_sun` / `d_sun`） |
| `ch02_mon.csv` | 第二章 浪漫 |
| `ch03_tue.csv` | 第三章 重装 |
| `ch04_wed.csv` | 第四章 宝瓶 |
| `ch05_thu.csv` | 第五章 榆木 |
| `ch06_fri.csv` | 第六章 我思故我在 |
| `ch07_gho.csv` | 第七章 幽灵／鲸／奥拉利乌姆 |
| `ch08_ear.csv` | 第八章 地球 |
| `event_solo.csv` / `event_calendar.csv` / `event_other.csv` | 个人事件、月次、开场／竞技场／结束 |
| `ui_sys.csv` / `ui_menu.csv` | 系统、菜单 |
| `dic.csv` | 图鉴 |
| `egg_*.csv` | 蛋怪对白 |
| `dungeon.csv` / `dungeon_other.csv` | 迷宫 |
| `battle.csv` | 王牌／头目／杂兵 |
| `generals.csv` | 将军卡片名 `gen_zeus`，兴趣 `gen_zeus#hobby` |

列都是 `id, jp, zh, notes, kind`。改某一章打开对应 csv；查或改一两行：

```
python3 tools/catalog_query.py get ev_sun_st65#0 gen_zeus
python3 tools/catalog_query.py prefix ev_sun
python3 tools/catalog_query.py search --sheet ch01_sun --zh 维纳斯
python3 tools/catalog_query.py set gen_no10 --zh '舒托拉斯曼'
```

其它对照表：

| 文件 | 用途 |
|---|---|
| `extracted/zh_keep.csv` | 假名输入表、图鉴假名索引、合言葉。zh 必须等于 jp，灌盘时不按中文重编码 |
| `extracted/zh_alphabet.csv` | 姓名输入格。jp 是和汉字共槽的旧字形（知/死/体…），zh 是 A–Z 和数字 |
| `extracted/zh_cmap.csv` | 字库映射（char, hex, glyph），不是文案 |

`kind`：`text` 译文 / `name` 将军名 / `hobby` 兴趣 / `keep` 保日文 / `alphabet` 姓名格 / `copy` 标点标记（zh 拷 jp） / `empty` 空串。

空 jp 保持空 zh。合言葉、假名表不要译成中文。专名跟 `GLOSSARY.txt`。

改完姓名格可以只改 `zh_alphabet.csv`，再跑：

```
python3 tools/apply_zh.py
```

它会把 alphabet 视图写回 catalog 分表，给每行补 kind，并刷新 keep / alphabet 两张视图。

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

运行时 6 套字库里，汉化替换的是 idx0 主 16×16 和 idx1 中等 16×16（对话气泡走 idx1，两套都是 n1=2760），以及两套 12×12。idx4 8bpp 彩字和 idx5 子集仍是日文。idx1 若截成 5 页（n1=1088），超出的汉字会回退成「あ」。

### 4. 灌盘

```
python3 tools/patch_iso.py
```

只换字库、不动 mes（例如把 idx1 从截断恢复成全表）可以：

```
python3 tools/patch_iso.py --fonts-only
```

只重编码开局情报板用的英雄／王国名（VFS 槽 0 加密子文件 4/5/9），不动 mes／字库：

```
python3 tools/patch_iso.py --slot0-names-only
```

将军卡片名（维纳斯 / 宙斯等）不在 mes 里，在 LBA 362 的 100 字节表。译文在 `generals.csv`，改完只跑：

```
python3 tools/patch_generals.py
```

不改 ELF，但仍须完全重启 PCSX2（不要读旧即时存档）。

`patch_iso.py` 做三件事：

1. **ELF 2 字节解码器**（VA `0x2DBDB8`，72 字节）  
   原版有死的 `mult a0,48`，加的却是 `a0`（delta−1）不是 LO，所以原盘 2 字节码实际是 `code = q + a0 − 16`。中文 bank1 远超这个范围，必须变成真的 ×48：

   `code = q + 48·a0 − 16`（再按范围 +192）

   补丁：nop 掉前面的 `mult v0,35`，用移位做 ×48（`sll 5` + `sll 4` + `addu`）。不要用紧挨着的 `mflo`（PCSX2 上 LO 不对，字形会全变成「あ」= id 0）；也不要把 `addu` 的 rd 写成 `$s0`（那是字符串指针，结果只显示第一个字）。

2. **字库包**（槽 49）  
   解开 F7+LZSS，换 idx0 / idx1 / idx2 / idx3，再压缩写回；放不下就追加扇区并改哈希。

3. **mes**  
   有 zh 的条目：保留原串首尾控制码，中间按 cmap 重编码（`mul48=True`）。  
   无 zh、或 KEEP_RAW（`sysmes_hiragana` / `sysmes_katakana` / `sysmes_dic_index_keyword` / `menu_secret_egg_word`）：只把旧 2 字节码转成新公式，字形号不变。  
   编码不能产出 NUL（mes 以 0 结尾）；`pack_trie` 必须保留原文件里的重复叶子。

4. **VFS 槽 0 实例名**（英雄／顾问、开局行星标题）  
   译文在 `extracted/catalog/instance.csv`（`inst_hero_*` / `inst_planet_*`），不要写进 Python。  
   子文件 5 是 7×84 英雄表（名在 +24），子文件 9 是 518×42 据点表（标题在 +12）。  
   盘上 XOR/t1 加密，按目录项解密后替换再写回。不要挂钩 PrintMes。

同时写 `extracted/SLPM_658.39` 和 ISO 里那份 ELF。ELF 一改，PCSX2 存档目录按 CRC 分，旧档对不上。

## 改译文之后怎么重灌

```
python3 tools/rebuild.py
```

它会：规范化 catalog → 扫一遍 zh 对 cmap，缺字就重建 KIWI → 灌 ELF/字库/mes → 灌将军表。默认会先关掉 PCSX2 再写盘（`--allow-pcsx2` 可强行在模拟器开着时写，不安全）。只检查缺字：

```
python3 tools/rebuild.py --check
```

完全退出再开 PCSX2，不要读旧即时存档。

分步（一般不必）：

1. `python3 tools/apply_zh.py`
2. 缺字时 `python3 tools/build_kiwi_font.py`
3. `python3 tools/patch_iso.py`（只换字库则 `--fonts-only`）
4. 只改将军名：`python3 tools/patch_generals.py`

## 故意没改的

| 内容 | 原因 |
|---|---|
| 大标题「半熟英雄４」 | TIM2 图，不是 mes |
| 合言葉 / 假名输入表 | 对照攻略、输入法 |
| NODATA / DUALSHOCK2 等 | 拉丁和日文汉字共槽，姓名输入另处理 |
| 音频 | 没动；没声是主机 HDMI 输出，不是盘 |

## 仓库里有什么

| 路径 | 作用 |
|---|---|
| `extracted/catalog/` | 原文 + 汉化分表（含将军名、槽 0 英雄／行星名）；`INDEX.txt` 是目录 |
| `extracted/zh_keep.csv` | 必须保留日文的对照表 |
| `extracted/zh_alphabet.csv` | 姓名输入格（字形共槽） |
| `extracted/GLOSSARY.txt` | 专名 |
| `extracted/zh_cmap.csv` | 字形映射 |
| `extracted/mes_file_index.csv` | mes LBA / 槽 |
| `tools/zh_csv.py` | 读 catalog 分表（不是译文本身） |
| `tools/catalog_query.py` | 按 id／前缀／分表查改译文 |
| `tools/apply_zh.py` | 规范化 catalog / keep／alphabet 视图 |
| `tools/extract_mes.py` | 从 ISO 抽出 mes，保留已有 zh |
| `tools/redecode_mes.py` | 改 SPECIAL 后重解 jp，保留 zh |
| `tools/mes_codec.py` | 编解码、NUL 回避、trie |
| `tools/lzss.py` | 游戏用 LZSS 解/压 |
| `tools/rebuild.py` | 一键规范化 + 补字库 + 灌盘 |
| `tools/patch_iso.py` | 解码器 + 字库 + mes + 槽 0 英雄／王国名灌盘 |
| `tools/patch_generals.py` | 将军卡片名灌盘 |
| `tools/build_kiwi_font.py` | 中文 KIWI |

ISO、ELF 转储、RAM、点阵 bin 都在 `.gitignore` 里。
