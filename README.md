# 半熟英雄4 中文化

PS2《半熟英雄4 ～7人の半熟英雄～》（SLPM-65839）文案 / 字库汉化。光盘 `半熟英雄4-7人的半熟英雄.iso` 不入库。

格式细节见 `extracted/RESOURCE_MAP.txt`，专名见 `extracted/GLOSSARY.txt`。

## 硬约束

- **日文汉字不能当中文用。** 原版 bank1 同一字形号会撞字（雄/四、始/言 等）。汉化必须重建 cmap，按中文重编码 mes。
- 空 jp 保持空 zh。不要用 `--force` 覆盖已填译文。
- 假名输入表、图鉴假名索引、合言葉保持原文（灌盘时也不重编码正文）。
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
    → extract_mes.py          抽出 mes，生成 catalog 的 jp
    → tools/zh_*.py           按 id 写中文
    → apply_zh.py             合并进 translation_catalog.csv
    → build_kiwi_font.py      按 zh 字符集出 cmap + KIWI 点阵
    → patch_iso.py            改 ELF 解码器、灌字库、重编码 mes、写 ISO
```

工作目录就是仓库根。脚本里的路径目前写死为本机 `/home/ubuntu/translation`。

### 1. 抽出文案

需要本机 ISO，以及一次 PCSX2 内存转储 `extracted/ram/eeMemory.bin`（导出字库、核对 sysmes）。

```
python3 tools/extract_mes.py
```

得到：

- `extracted/mes/*.bin` — 光盘 / RAM 里的 mes
- `extracted/text/` — 解码预览
- `extracted/translation_catalog.csv` — `id,jp,zh,notes`（约 24468 条）

`id` 是 mes 的 ASCII key；同一 key 多行时为 `key#0`、`key#1`…。解码规则在 `tools/mes_codec.py`：字节 ×189 mod 256 还原；1 字节码 0–191 为假名 bank0；2 字节码在范围内再 +192 进 bank1。

改 `SPECIAL` 撞字表后，只重解文本、不改 ISO：

```
python3 tools/redecode_mes.py
```

### 2. 写中文

译文不直接手改 CSV（再跑 apply 会被跳过已填行，但包才是源）。按文件往 `tools/zh_*.py` 的 `by_id()` 里加条目，专名跟 `GLOSSARY.txt`。

```
python3 tools/apply_zh.py
```

合并顺序：`fill_generated()` → 各包 `by_id()` → `copy_jp_prefixes()`（假名表等原样拷 jp）→ `by_jp()`（整句 UI 对译）。已有 zh 默认保留。

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

1. 改 `tools/zh_*.py`（或 glossary）
2. `python3 tools/apply_zh.py`
3. 若出现了 cmap 里没有的新字：`python3 tools/build_kiwi_font.py`
4. `python3 tools/patch_iso.py`
5. 用本机 ISO 开 PCSX2（不要 `--force`）

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
| `extracted/translation_catalog.csv` | 文案总表 |
| `extracted/GLOSSARY.txt` | 专名 |
| `extracted/zh_cmap.csv` | 当前字形映射 |
| `extracted/mes_file_index.csv` | mes LBA / 槽 |
| `tools/mes_codec.py` | 编解码、NUL 回避、trie |
| `tools/lzss.py` | 游戏用 LZSS 解/压 |
| `tools/patch_iso.py` | 解码器 + 字库 + mes 灌盘 |
| `tools/build_kiwi_font.py` | 中文 KIWI |
| `tools/zh_*.py` | 分文件译文 |
| `tools/apply_zh.py` | 合并译文 |

ISO、ELF 转储、RAM、点阵 bin 都在 `.gitignore` 里。
