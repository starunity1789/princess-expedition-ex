# The Princesses' Expedition EX · 皇女的远征军EX

**[English](#english) · [中文](#中文)**

---

## English

A Stellaris (4.5.*) mod: the new origin **The Princesses' Expedition**, plus a rim cluster for the expedition, five guaranteed great powers and a set of galaxy rules.

- Steam Workshop: [The Princesses' Expedition EX](https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893)
- Setting: [The Stargazer Project](https://github.com/starunity1789/StargazerPR)

### The setting

The four princesses come from the **Empire of AllLife Chance-Born** (CNP8) on the Deepwinter Continent of the Grove Between Stars, the world of The Stargazer Project. The Empire is ruled by the Dim King, the first true immortal of that world, under a Philosopher-King Authoritarian Democracy, and leads the four-nation alliance of the Elves, AllLife Chance-Born, the United States of Winter and Kappa Heavy Industries.

This mod takes place **before the Dim King disappeared**. The Empire achieved its technological breakthrough alone, yet its homeworld remained divided. The Emperor stayed behind, and his four daughters took the mobile fortress "Origin Fortress" to the stars to found the Empire anew. Their colonists fell to an incurable illness and can no longer bear children, so the princesses lead their people down the path of synthetic fertility.

The first three great powers added by EX are tied to the Empire too: the Burning White Stag Legion is a machine army built by the Elves, the Empire's allies; the Far Star Alliance is made up of other elites and nations from the Empire's homeworld; and the Grand Suzerain Allied Fief is merely a rural fief of a feudal civilization spread across the universe. Since 2.5 two genocidal empires join them: the hive Tide of Dread and the machine Terminal Alignment Protocol.

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
- **Name list "苍神缘起帝国" (AllLife Chance-Born)**: 24 clans with three-part names "clan=name=epithet" (2,304 in all), dedicated ship and class names for every vanilla hull, fleets and armies numbered as "帝国第N舰队/军团"; selectable by any empire, shown in Chinese in all ten UI languages
- **Preset empire "Empire of AllLife Chance-Born"**: this origin with the name list above, Fanatic Authoritarian and Materialist, Philosopher King and Technocracy - pick it directly on the empire selection screen

**New in EX**
- **Rim cluster**: at game start the expedition moves to 7 systems beyond the galaxy rim at 12 o'clock (Origin's Reach, the L-Gate at Starsea Firefly, a pre-FTL world at Formless Link, a black hole, a neutron star, a pulsar, and the Relic World of the Great Inheritor), linked to the galaxy by a single hyperlane. Origin's Reach itself holds a second L-Gate and a Ruined Mega Shipyard, and the capital gains the High Elemental Sealing Institute (+1,000,000 storage, +2 minor artifacts per month)
- **Five guaranteed great powers**, each beyond the rim with a fixed empire flag and a fixed monthly supply; all start with +1000 naval capacity, +10 starbase capacity, a level-10 immortal admiral, doubled pop growth on their homeworlds for 20 years, and 10 extra agriculture, generator and mining districts each on every non-machine homeworld:
  - Burning White Stag Legion (10:30): Ascensionists, Rapid Replicators, OTA Updates; an L-Gate in the home system
  - Far Star Alliance (5 o'clock): MegaCorp, Fanatic Militarist + Spiritualist; Private Prospectors, Corporate Crafters, Naval Contractors; Psionic Ascension; starts with the Psionic Archive relic; an L-Gate in the home system
  - Grand Suzerain Allied Fief (3 o'clock): Fanatic Purifiers, Feudal Realm, Distinguished Admiralty; +12% research speed; its six tomb worlds carry a +55% habitability floor; Genetic Ascension (Purity); AI full rights; always takes Cosmogenesis; joins the Galactic Community
  - Tide of Dread (9 o'clock, new): Devouring Swarm, One Mind, Subspace Ephapse; three start-sized homeworlds and a Ruined Aetherophasic Engine; always Becomes the Crisis
  - Terminal Alignment Protocol (6:30, new): Determined Exterminators, Warbots, Experience Cache; four start-sized machine worlds; always Becomes the Crisis; joins the Galactic Community until Crisis level 5
- **Galaxy rules**: The Chosen (always at 8 o'clock) and the crash site of Keides, Scion of Vagros always spawn; Mega Shipyards have 50 shipyard slots; Galactic Community sessions and recesses take half as long; +100K storage for all empires; doubled base hull for non-bio ships; every vanilla shield and armor value doubled; no hologram effect on council portraits
- **Bundled portraits**: the Ancient Dragonkin and Kemonomimi animated portrait packs are merged in - disable the standalone packs if you are subscribed to them

Full details: [workshop description (English)](docs/workshop_description_en.txt).

### Repository layout

```
mod/      the mod itself (this folder is what gets uploaded to the Workshop)
tools/    generator scripts (Python 3 + Pillow) and the name-list source data
art/      portraits, empire flag logos, cover and relic artwork
docs/     Workshop descriptions (English and Chinese), the name-list overview, and the PD/GPM/Stellar AI merge plan
```

`mod/` is linked into the game's mod folder with a directory junction, so `.git` never reaches the Workshop. See the Chinese section below for development, testing and publishing notes.

### Required DLC

The Machine Age and Ancient Relics (origin); Distant Stars (L-Gate); First Contact (The Chosen); Synthetic Dawn, MegaCorp, Astral Planes, Necroids, Nemesis and BioGenesis (great powers); Galactic Paragons recommended.

---

## 中文

群星（Stellaris 4.5.*）MOD。新起源「皇女的远征军」，外加银河边缘的远征军星团、五个保底列强和一组银河规则。

- Steam 创意工坊：[皇女的远征军EX](https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893)
- 世界观：[观星者计划 / The Stargazer Project](https://github.com/starunity1789/StargazerPR)

### 故事背景

四位皇女来自观星者计划中星间林地凛冬大陆的**苍神缘起帝国**（CNP8）。帝国由星间林地第一位真正意义上的永生者——黯王统治，实行哲人王威权民主制，是精灵-苍神缘起-凛冬合众国-河童重工四国同盟中的主导国家。

本 MOD 的故事发生在**黯王失踪之前**：帝国独自突破了高等科技，但母星依旧四分五裂。皇帝留守母星，四位皇女驾驶移动要塞「起源要塞」远赴群星，为帝国开辟新的根基。随行的殖民者水土不服、身患绝症，再也无法繁衍，皇女们只能带领族人走上合成繁衍之路。

EX 最早的三个列强也与帝国有关：燃烧白鹿军团是帝国盟友精灵族制造的机器人军团，远星同盟组织由帝国母星上的其他精英与国家组成，大君主同盟领地则是一个遍布宇宙的高等封建文明的乡村领地。2.5 又加入了两个灭绝政体：虫巢「恐惧之潮」与机械智能「终端对齐协议」。

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
- **名称集「苍神缘起帝国」**：24 个部落姓，人名为「部落姓=个人名=长名」（共 2304 个）；原版每种舰体都有专属舰名与舰级，舰队、陆军编号为「帝国第N舰队/军团」。任何帝国都能选用，10 种界面语言都显示中文
- **预设帝国「苍神缘起帝国」**：皇女的远征军起源 + 上面的名称集，狂热威权 + 唯物，哲人王 + 技术官僚，开局界面直接可选

**EX 新增**
- **边缘星团**：开局远征军整体搬到银河 12 点方向外的 7 个星系（起源之地、星海萤火 L 星门、无形链接土著、极限边缘黑洞、辉煌耀世中子星、窒息瑶光脉冲星、大传承者遗落星球），只有大传承者一条航道通往银河。起源之地本身还有第二座 L 星门和一座毁坏的巨型船坞，首都多一处特殊地形「高位元素秘封研究院」（储存上限 +1000000、每月文物 +2）
- **五个保底列强**，各在银河边缘外，有固定的帝国标识和固定补给；开局都有海军容量 +1000、恒星基地上限 +10，初始 30 艘护卫舰一支舰队、带一位 10 级永生舰队司令，母星 20 年内人口增长翻倍；非机械星球的开局母星再加农业、发电、采矿区划各 10 个：
  - 燃烧白鹿军团（10 点半）：升格假设、快速复制者、空中下载升级；母星系一座 L 星门
  - 远星同盟组织（5 点）：巨型企业，极端军国 + 唯心；民营勘探者、巧手公司、舰队承包商；灵能飞升；开局获得遗珍「灵能档案」；母星系一座 L 星门
  - 大君主同盟领地（3 点）：种族洁癖、封建社会、卓越海军；研究速度 +12%；星团里 6 颗死寂星球的宜居度下限 +55%；基因飞升（纯净）；人工智能公民权；必选宇宙创生；加入星海共同体
  - 恐惧之潮（9 点，新增）：噬杀蜂群、唯一意志、亚空间突触；三颗开局规格的母星，母星系有一座损坏的以太相引擎；必选星海天罚
  - 终端对齐协议（6 点半，新增）：铁心灭绝者、战争机器、经验缓存器；四颗开局规格的机械星球母星；必选星海天罚；加入星海共同体（星海天罚第 5 级时照原版被踢出）
- **银河规则**：所有帝国开局就有居住站科技（轨道居住站及其两级扩建）；必定生成天选民（固定在 8 点）和凯德斯（瓦格罗之子嗣）的坠毁点；巨型船坞的船坞数量改为 50；星海共同体的议程与休会时间减半；所有国家存储上限 +100K；非生物船基础舰体翻倍；原版所有能量盾和装甲数值翻倍；议会肖像去掉全息效果
- **内置肖像包**：已合并 Ancient Dragonkin（龙族）与 Kemonomimi（兽耳）两套动态肖像包——如果还订阅着这两个独立包，请停用它们

**内置三个 MOD（2.8 起）**——由 `tools/merge_upstream.py` 合并、裁剪，**启动器里必须停用独立的这三个 MOD**，否则同一批定义会出现两份：
- **Planetary Diversity**：113 个新行星类型与新气候宜居性特质，连同行星生成引擎、改造链路、行星类型界面。删去全部岗位与区域修改、飞升世界、穹顶殖民地、起源与公民覆盖等非行星类型内容
- **Guilli's Planet Modifiers and Features**：635 个行星修正、216 个行星地貌与 21 个遗珍，连同修正调度引擎。删去遗珍战争/窃取/交易、前驱者考古、行星决议、游牧民族、内容事件、环境物件等其余全部内容；开局不再弹设置菜单，直接按默认设置运行
- **Stellar AI**：原样内置
- 新增玩家首都决议 **「探寻遗珍」**：花 10000 能量币随机获得一件尚未拥有的 GPM 遗珍，直到 21 件全部获得

完整说明见工坊简介原文：[中文](docs/workshop_description_zh.txt) / [English](docs/workshop_description_en.txt)。

### 目录结构

```
mod/      MOD 本体（上传工坊的就是这个文件夹）
tools/    生成脚本，以及名称集的源数据 cgen_names_source.json；upstream_manifest.json 记录合并进来的上游文件
art/      立绘、列强帝国标识 LOGO、封面、遗珍原图
docs/     工坊简介原文（中文、英文各一份），名称集总览与全部人名，三方整合方案
```

合并进来的上游**二进制资源**（约 2 GB，几乎全是 PD 的行星贴图）**不进 git**：`.gitignore` 末尾有一段由
`merge_upstream.py` 生成的精确文件清单。重新 clone 之后要先订阅那三个 MOD，再跑一次
`python tools/merge_upstream.py ...` 把贴图拷回来，MOD 才完整。脚本与本地化照常进 git。

`mod/` 通过目录联接（junction）挂到游戏的 MOD 目录：

```
文档\Paradox Interactive\Stellaris\mod\atb_princess_expedition_ex  →  本仓库\mod
```

游戏和启动器看到的路径不变；`.git` 在 `mod/` 之外，不会被传到工坊。

联接不在时（换机器、重新 clone 之后）用 cmd 重建，不需要管理员权限：

```
mklink /J "%USERPROFILE%\Documents\Paradox Interactive\Stellaris\mod\atb_princess_expedition_ex" "%USERPROFILE%\Documents\GitHub\princess-expedition-ex\mod"
```

启动器还需要同目录下一个 `atb_princess_expedition_ex.mod` 描述文件指向这个联接：内容照抄
`mod/descriptor.mod`，再加一行 `path="mod/atb_princess_expedition_ex"`。

> ⚠️ **这个描述文件只在上传时放进 MOD 目录，传完立刻移走。**
> 它和订阅版的 `ugc_3821602893.mod` 都带 `remote_file_id="3821602893"`，两个描述文件抢同一个
> 工坊编号时，**游戏会直接不加载这个 MOD**：起源、肖像、数值全部失效，而且启动器不报错、
> error.log 里也只会看到 `Invalid government origin` 和
> `portrait ... is not found in portrait set database` 这类下游症状，很难往这上面想。
> 平时把它改名成 `atb_princess_expedition_ex.mod.disabled` 放在 MOD 目录外面即可。

### 文件前缀

| 前缀 | 内容 |
|---|---|
| `atb_` | 起源、四位皇女、搬家后的星团 |
| `atbgp_` | 五个保底列强（全部由 `tools/gen_great_powers.py` 生成，不要手改） |
| `atb_ex_` | 银河规则、天选民、凯德斯、搬家流程 |
| `adpp_` | 合并进来的 Ancient Dragonkin 肖像包，原样保留，不要改 |
| `kmpp_` | 合并进来的 Kemonomimi 肖像包，原样保留，不要改 |
| `cgen_` / `CGEN_` | 名称集「苍神缘起帝国」（全部由 `tools/gen_names.py` 生成，不要手改；2.6 起由独立 MOD「苍神缘起帝国·名称集 0.1.0」并入） |
| `gpm_` | 合并进来的 Guilli's Planet Modifiers（由 `tools/merge_upstream.py` 写入，不要手改，改 `KEEP` / `PATCHES` 后重跑） |
| `pd_` / `pdengine` / `!vanilla_*_fix` | 合并进来的 Planetary Diversity（同上） |
| `stellarai_` / `~stellarai_` / `111_stellarai` | 合并进来的 Stellar AI（同上） |
| `atb_relic_quest_` | 决议「探寻遗珍」（由 `tools/gen_relic_quest.py` 生成，不要手改） |

上游文件的完整清单与来源见 `tools/upstream_manifest.json`。除了上面这些前缀，上游还以原版同名路径覆盖了一批原版文件，见下文「覆盖的原版文件」。

### 开发

需要 Python 3 和 Pillow。

```bash
# 重新生成保底列强的全部脚本和本地化
python tools/gen_great_powers.py mod

# 把两位列强元首的立绘转成游戏肖像（半身 + 全身）
python tools/make_portraits.py art/great_power_rulers mod <预览输出文件夹>

# 生成遗珍、起源图标、事件图和缩略图
python tools/make_art.py art mod <预览输出文件夹>

# 生成三个列强的帝国标识图标（128x128 DDS）
python tools/make_flags.py art/great_power_flags mod

# 把原版所有能量盾和装甲的数值翻倍（倍率可选，默认 2）
python tools/gen_double_defenses.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 重新生成巨型船坞（50 个船坞）与关掉原版天选民随机生成的两份覆盖文件
python tools/gen_vanilla_patches.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 把两套内置肖像包挂进原版的 portrait_sets（覆盖原版同名文件）
python tools/gen_portrait_sets.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 重新生成名称集「苍神缘起帝国」（改名字改 tools/cgen_names_source.json）
python tools/gen_names.py mod docs

# 把 PD / GPM / Stellar AI 按保留清单合并进 mod/（需要三者都已订阅）
# 校验没通过时什么都不写；上游改了结构会在这里报错，按提示调整脚本里的 KEEP / PATCHES
python tools/merge_upstream.py "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990" mod

# 重新生成决议「探寻遗珍」（遗珍清单读合并后的 mod/common/relics/gpm_relics*.txt，合并之后跑）
python tools/gen_relic_quest.py mod

# 静态自检：括号配对、本地化格式、贴图引用、原版 ID、本次改动点、三方整合
python tools/check_mod.py
```

**测试**：把 `文档\Paradox Interactive\Stellaris\dlc_load.json` 改成只启用本 MOD，直接运行 `stellaris.exe -gdpr-compliant`，读 `logs/error.log`。判断加载成功要确认游戏进程还在、`crashes` 文件夹没有新的崩溃报告——日志停止增长不代表没有崩溃。

**覆盖的原版文件**（游戏更新后需要对照新版原版重做）：
- `common/governments/authorities/00_authorities.txt`
- `common/species_rights/living_standards/00_living_standards.txt`
- `events/origin_events_paragon.txt`
- `gfx/FX/buttonstate_rendertarget_hologram.shader`
- `common/solar_system_initializers/atb_ex_initializers.txt`（原版传奇领袖坠毁点的副本）
- `common/scripted_variables/02_scripted_variables_component_cost.txt`（护盾装甲翻倍，跑 `gen_double_defenses.py` 重做即可）
- `common/megastructures/11_mega_shipyard.txt`、`events/ancient_relics_arcsite_events_2.txt`（巨型船坞 50 个船坞、关掉原版天选民随机生成，跑 `gen_vanilla_patches.py` 重做即可）
- `common/defines/atb_ex_defines.txt`（只覆盖星海共同体的三项计时，原版改了数值时对照调整）
- `common/game_rules/atb_rules.txt` 里的 `can_be_part_of_galactic_community`、`can_dismiss_leader`（原版同名规则的副本）
- `common/portrait_sets/00_portrait_sets.txt`（把两套肖像包挂进原版集合，跑 `gen_portrait_sets.py` 重做即可）

2.8 起合并进来的上游另外覆盖了 42 个原版文件（Stellar AI 27 个、Planetary Diversity 15 个；GPM 不覆盖原版路径），
清单见 `docs/整合方案.md` §1.1。四方之间没有任何两家覆盖同一个原版文件。游戏更新后有两种做法：
等上游作者更新、重新订阅后重跑 `merge_upstream.py`；或者自己对照新版原版改 `mod/` 里的这些文件
（改完后重跑 `merge_upstream.py` 会把它们覆盖回上游版本，所以自维护时要把改动做进脚本的 `PATCHES`）。

### 发布到工坊

1. 从 Steam 启动群星（单游戏启动器），进入「Mod 库 → 上传 MOD」，选「皇女的远征军EX」，上传到「Steam 创意工坊」。Mod ID 应自动显示 3821602893。
2. 上传前把 `docs/workshop_description_en.txt` 的内容贴进描述栏——上传会用这一栏覆盖工坊的默认（英语）简介。
3. 上传后到工坊物品页「编辑标题与描述」，语言选「简体中文」，标题填「皇女的远征军EX」，描述贴 `docs/workshop_description_zh.txt`。中文 Steam 的玩家看中文版，其他语言的玩家看英文版。
4. 简介上限 8000 字节（UTF-8），两份各自计算。**注意按 CRLF 算**：网页表单会把换行转成 CRLF，
   仓库里的文件是 LF，所以实际占用 = 文件字节数 + 行数。超了只会弹「保存标题和描述时出现错误」，
   不提示是长度问题。核对命令：
   ```bash
   python -c "import pathlib;t=pathlib.Path('docs/workshop_description_zh.txt').read_text(encoding='utf-8');print(len(t.replace(chr(10),chr(13)+chr(10)).encode()))"
   ```
5. 启动器上传时填的描述只写进工坊的**英文**简介，而且实测不一定生效；稳妥做法是上传后到物品页
   「编辑标题与描述」里分别保存英文和简体中文两份。
6. 如果提示「已存在具有相同远程 ID 的本地 Mod」，是启动器数据库 `launcher-v2.sqlite` 里别的本地条目还登记着这个编号：关掉启动器，把那些条目的 `remoteSteamId` 清空即可。
7. 更新后 Steam 会自动做内容检查，期间物品暂时隐藏，通过后自动恢复。
8. **把工坊物品设为私密**（2.1 起必做，因为合并了他人的肖像包）：浏览器打开
   <https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893>，右侧栏点「更改可见性 / Change Visibility」，
   选「私密 / Private」。私密之后只有物品作者本人能看到和订阅，好友也看不到。
   上传新版本不会改动已设好的可见性，所以只需要设一次。
9. **上传成功后，在启动器里停用独立的两个肖像包**（Ancient Dragonkin 3765752651、Kemonomimi 3821158186），
   否则同一批肖像会被定义两次。本 MOD 没上传完之前先别停用，不然游戏里会直接少掉这些肖像。

### 内置的第三方内容

本 MOD 合并了两套他人制作的动态肖像包，文件原样保留（`adpp_` / `kmpp_` 前缀，以及
`gfx/models/portraits/adpp_ancient_dragonkin`、`gfx/models/portraits/kmpp_kemonomimi`）：

| 肖像包 | 工坊 ID | 本 MOD 里的用途 |
| --- | --- | --- |
| Ancient Dragonkin Animated Portrait Pack | 3765752651 | 爬行类、炼狱类可选；「无形链接」的前超光速土著固定使用 |
| Kemonomimi Animated Portrait Pack | 3821158186 | 哺乳类、机器人、机械可选；燃烧白鹿军团固定使用 |

更新这两套素材时，直接从对应工坊目录整体覆盖同名文件即可，但 `common/portrait_sets/` 下那两个文件要重做下面这步改名。

**两个原包的 `common/portrait_sets/` 文件没有采用，不要拷进来。** 它们各自用 `mammalians`、
`reptilians` 这类原版已有的集合名另开文件，实测在 4.5.2 下不生效，游戏日志报
`portrait '...' is not found in portrait set database`，肖像在游戏里根本不出现
（改成独立集合名再注册进 `portrait_categories` 也一样没用）。

改为整文件覆盖原版 `common/portrait_sets/00_portrait_sets.txt`，把肖像组直接追加进原版已有的集合，
由 `tools/gen_portrait_sets.py` 生成：

| 原版集合 | 追加的肖像组 |
| --- | --- |
| `mammalians` | `kmpp_kemonomimi` |
| `machines` / `robots` | `kmpp_kemonomimi_machine` |
| `reptilians` | `adpp_ancient_dragonkin` |
| `infernals` | `adpp_ancient_dragonkin_inf` |

玩家如果同时订阅了这两个独立包，需要停用它们，否则同一批肖像会被定义两次。

### 需要的 DLC

机械纪元、远古遗珍（起源必需）；远星（L 星门）；首次接触（天选民）；合成黎明、巨企、星界风云、死灵物种包、复仇女神、生物创世（列强）；银河英杰（推荐）。
