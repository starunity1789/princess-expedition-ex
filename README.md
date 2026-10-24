# The Princesses' Expedition EX · 皇女的远征军EX

**[English](#english) · [中文](#中文)**

---

## English

A Stellaris (4.5.*) mod: the new origin **The Princesses' Expedition**, plus a rim cluster for the expedition, three guaranteed great powers and a set of galaxy rules.

- Steam Workshop: [The Princesses' Expedition EX](https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893)
- Setting: [The Stargazer Project](https://github.com/starunity1789/StargazerPR)

### The setting

The four princesses come from the **Empire of AllLife Chance-Born** (CNP8) on the Deepwinter Continent of the Grove Between Stars, the world of The Stargazer Project. The Empire is ruled by the Dim King, the first true immortal of that world, under a Philosopher-King Authoritarian Democracy, and leads the four-nation alliance of the Elves, AllLife Chance-Born, the United States of Winter and Kappa Heavy Industries.

This mod takes place **before the Dim King disappeared**. The Empire achieved its technological breakthrough alone, yet its homeworld remained divided. The Emperor stayed behind, and his four daughters took the mobile fortress "Origin Fortress" to the stars to found the Empire anew. Their colonists fell to an incurable illness and can no longer bear children, so the princesses lead their people down the path of synthetic fertility.

The three great powers added by EX are tied to the Empire too: the Burning White Stag Legion is a machine army built by the Elves, the Empire's allies; the Far Star Alliance is made up of other elites and nations from the Empire's homeworld; and the Grand Suzerain Allied Fief is merely a rural fief of a feudal civilization spread across the universe.

### The four princesses

The characters - their personalities, looks and every detail - were designed by the author in 2022; the portraits were drawn by AI from those designs.

| | Character | Role | Design |
|---|---|---|---|
| First Princess | Filiruoya | Ruler, Commander | Traditional Chinese dress with modern touches |
| Second Princess | Yugudora | Minister of Defense, Commander | A blend of three East Asian cultures, down to the wooden geta on her feet |
| Third Princess | Youfeilina | Head of Research, Scientist | Robes of the *xiuxian* cultivation world popular in China today |
| Fourth Princess | Antaixiya | Minister of State, Official | Western style |

### Features

**Origin: The Princesses' Expedition**
- Includes every mechanic of vanilla Synthetic Fertility; Synthetic Ascension only
- Capital: the Origin Fortress, a size-25 giant mobile habitat; the four princesses serve as Ruler and Councilors
- Decisions "Establish the Expeditionary Order" and "Explore the Secrets of the Precursors", the Dreadnoughts tech, and the relic "Seal of the Princess Guard"

**New in EX**
- **Rim cluster**: at game start the expedition moves to 7 systems beyond the galaxy rim at 2 o'clock (Origin's Reach, the L-Gate at Starsea Firefly, a pre-FTL world at Formless Link, a black hole, a neutron star, a pulsar, and the Relic World of the Great Inheritor), linked to the galaxy by a single hyperlane
- **Three guaranteed great powers**: Burning White Stag Legion (11 o'clock), Far Star Alliance (5 o'clock) and Grand Suzerain Allied Fief (9 o'clock), each with its own cluster beyond the rim and a fixed monthly supply
- **Galaxy rules**: The Chosen and the crash site of Keides, Scion of Vagros always spawn; +100K storage for all empires; doubled base hull for non-bio ships; no hologram effect on council portraits

Full details: [workshop description (English)](docs/workshop_description_en.txt).

### Repository layout

```
mod/      the mod itself (this folder is what gets uploaded to the Workshop)
tools/    generator scripts (Python 3 + Pillow)
art/      portraits, cover and relic artwork
docs/     Workshop descriptions (English and Chinese)
```

`mod/` is linked into the game's mod folder with a directory junction, so `.git` never reaches the Workshop. See the Chinese section below for development, testing and publishing notes.

### Required DLC

The Machine Age and Ancient Relics (origin); Distant Stars (L-Gate); First Contact (The Chosen); Synthetic Dawn, MegaCorp, Necroids and Nemesis (great powers); Galactic Paragons recommended.

---

## 中文

群星（Stellaris 4.5.*）MOD。新起源「皇女的远征军」，外加银河边缘的远征军星团、三个保底列强和一组银河规则。

- Steam 创意工坊：[皇女的远征军EX](https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893)
- 世界观：[观星者计划 / The Stargazer Project](https://github.com/starunity1789/StargazerPR)

### 故事背景

四位皇女来自观星者计划中星间林地凛冬大陆的**苍神缘起帝国**（CNP8）。帝国由星间林地第一位真正意义上的永生者——黯王统治，实行哲人王威权民主制，是精灵-苍神缘起-凛冬合众国-河童重工四国同盟中的主导国家。

本 MOD 的故事发生在**黯王失踪之前**：帝国独自突破了高等科技，但母星依旧四分五裂。皇帝留守母星，四位皇女驾驶移动要塞「起源要塞」远赴群星，为帝国开辟新的根基。随行的殖民者水土不服、身患绝症，再也无法繁衍，皇女们只能带领族人走上合成繁衍之路。

EX 新增的三个列强也与帝国有关：燃烧白鹿军团是帝国盟友精灵族制造的机器人军团，远星同盟组织由帝国母星上的其他精英与国家组成，大君主同盟领地则是一个遍布宇宙的高等封建文明的乡村领地。

### 四位皇女

四位角色的内在设定、外貌与全部细节由作者于 2022 年构想完成；立绘根据作者的设计由 AI 绘制。

| | 角色 | 职位 | 设计来源 |
|---|---|---|---|
| 第一皇女 | 菲莉若雅 | 统治者 · 指挥官 | 中国传统服饰，加以现代改良 |
| 第二皇女 | 尤古朵拉 | 国防部长 · 指挥官 | 东亚三国文化的融合，脚下穿的是木屐 |
| 第三皇女 | 幽妃丽娜 | 科学部长 · 科学家 | 当代中国流行的修真体系服饰 |
| 第四皇女 | 安泰熙雅 | 国务卿 · 行政官 | 西方风格 |

### 主要内容

**起源：皇女的远征军**
- 融合原版合成繁衍的全部机制，只能走机械飞升
- 首都是规模 25 的超大型移动居住站「起源要塞」，四位皇女担任统治者和议会要职
- 决议「确立远征军体制」「探索先驱者文明的秘密」，科技「无畏舰」，遗珍「皇女亲卫队印章」

**EX 新增**
- **边缘星团**：开局远征军整体搬到银河 2 点钟方向外的 7 个星系（起源之地、星海萤火 L 星门、无形链接土著、极限边缘黑洞、辉煌耀世中子星、窒息瑶光脉冲星、大传承者遗落星球），只有大传承者一条航道通往银河
- **三个保底列强**：燃烧白鹿军团（11 点）、远星同盟组织（5 点）、大君主同盟领地（9 点），各在银河边缘外有自己的星团和固定补给
- **银河规则**：必定生成天选民和凯德斯（瓦格罗之子嗣）的坠毁点；所有国家存储上限 +100K；非生物船基础舰体翻倍；议会肖像去掉全息效果

完整说明见工坊简介原文：[中文](docs/workshop_description_zh.txt) / [English](docs/workshop_description_en.txt)。

### 目录结构

```
mod/      MOD 本体（上传工坊的就是这个文件夹）
tools/    生成脚本
art/      立绘、封面、遗珍原图
docs/     工坊简介原文（中文、英文各一份）
```

`mod/` 通过目录联接（junction）挂到游戏的 MOD 目录：

```
文档\Paradox Interactive\Stellaris\mod\atb_princess_expedition_ex  →  本仓库\mod
```

游戏和启动器看到的路径不变；`.git` 在 `mod/` 之外，不会被传到工坊。

### 文件前缀

| 前缀 | 内容 |
|---|---|
| `atb_` | 起源、四位皇女、搬家后的星团 |
| `atbgp_` | 三个保底列强（全部由 `tools/gen_great_powers.py` 生成，不要手改） |
| `atb_ex_` | 银河规则、天选民、凯德斯、搬家流程 |

### 开发

需要 Python 3 和 Pillow。

```bash
# 重新生成保底列强的全部脚本和本地化
python tools/gen_great_powers.py mod

# 把两位列强元首的立绘转成游戏肖像（半身 + 全身）
python tools/make_portraits.py art/great_power_rulers mod <预览输出文件夹>

# 生成遗珍、起源图标、事件图和缩略图
python tools/make_art.py art mod <预览输出文件夹>
```

**测试**：把 `文档\Paradox Interactive\Stellaris\dlc_load.json` 改成只启用本 MOD，直接运行 `stellaris.exe -gdpr-compliant`，读 `logs/error.log`。判断加载成功要确认游戏进程还在、`crashes` 文件夹没有新的崩溃报告——日志停止增长不代表没有崩溃。

**覆盖的原版文件**（游戏更新后需要对照新版原版重做）：
- `common/governments/authorities/00_authorities.txt`
- `common/species_rights/living_standards/00_living_standards.txt`
- `events/origin_events_paragon.txt`
- `gfx/FX/buttonstate_rendertarget_hologram.shader`
- `common/solar_system_initializers/atb_ex_initializers.txt`（原版传奇领袖坠毁点的副本）



### 需要的 DLC

机械纪元、远古遗珍（起源必需）；远星（L 星门）；首次接触（天选民）；合成黎明、巨企、死灵物种包、复仇女神（三个列强）；银河英杰（推荐）。
