# The Princesses' Expedition EX · 皇女的远征军EX

**[English](#english) · [中文](#中文)**

---

## English

A Stellaris (4.6.*) mod: the new origin **The Princesses' Expedition**, plus a rim cluster for the expedition, five guaranteed great powers and a set of galaxy rules.

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
- Since 3.15 also merges the academy and leader training of **Golden Generation** (Willpower DLC, ideologies enabled in setup): a Golden Academy on the homeworld, a generation of leaders trained through the Golden Generation event chain, and after graduation the academy can become an Elite Academy or a Golden Museum; the Golden Generation ideology part (tenets, codifying the ideology) is not included
- Includes every mechanic of vanilla Synthetic Fertility; Synthetic Ascension only
- Capital: the Origin Fortress, a size-25 giant mobile habitat; the four princesses serve as Ruler and Councilors
- Decisions "Establish the Expeditionary Order" and "Explore the Secrets of the Precursors", the Dreadnoughts tech, and the relic "Seal of the Princess Guard"
- **Name list "苍神缘起帝国" (AllLife Chance-Born)**: 24 clans with three-part names "clan=name=epithet" (2,304 in all), dedicated ship and class names for every vanilla hull, fleets and armies numbered as "帝国第N舰队/军团"; selectable by any empire, shown in Chinese in all ten UI languages
- **Preset empire "Empire of AllLife Chance-Born"**: this origin with the name list above, Fanatic Authoritarian and Materialist, Philosopher King and Technocracy - pick it directly on the empire selection screen

**New in EX**
- **Rim cluster**: at game start the expedition moves to 7 systems beyond the galaxy rim at 12 o'clock (Origin's Reach, the L-Gate at Starsea Firefly, a pre-FTL world at Formless Link, a black hole, a neutron star, a pulsar, and the Relic World of the Great Inheritor), linked to the galaxy by a single hyperlane. Origin's Reach itself holds a second L-Gate and a Ruined Mega Shipyard, and the capital gains the High Elemental Sealing Institute (+1,000,000 storage, +2 minor artifacts per month)
- **Five guaranteed great powers**, each beyond the rim with a fixed empire flag and a fixed monthly supply; all start with +300 naval capacity, +10 starbase capacity, a level-10 immortal admiral, doubled pop growth on their homeworlds for 20 years, and 10 extra agriculture, generator and mining districts each on every non-machine homeworld:
  - Burning White Stag Legion (10:30): Ascensionists, Rapid Replicators, OTA Updates; an L-Gate in the home system
  - Far Star Alliance (5 o'clock): MegaCorp, Fanatic Militarist + Spiritualist; Gospel of the Masses, Corporate Crafters, Naval Contractors; Psionic Ascension; starts with the Psionic Archive relic; an L-Gate in the home system
  - Grand Suzerain Allied Fief (3 o'clock): Fanatic Purifiers, Feudal Realm, Distinguished Admiralty; +12% research speed; its six tomb worlds carry a +55% habitability floor; Genetic Ascension (Purity); AI full rights; always takes Cosmogenesis; joins the Galactic Community
  - Tide of Dread (9 o'clock, new): Devouring Swarm, One Mind, Subspace Ephapse; three start-sized homeworlds and a Ruined Aetherophasic Engine; always Becomes the Crisis
  - Terminal Alignment Protocol (6:30, new): Determined Exterminators, Warbots, Experience Cache; four start-sized machine worlds; always Becomes the Crisis; joins the Galactic Community until Crisis level 5
- **Galaxy rules**: The Chosen (always at 8 o'clock) and the crash site of Keides, Scion of Vagros always spawn; Mega Shipyards have 50 shipyard slots; Galactic Community sessions and recesses take half as long; +100K storage for all empires; doubled base hull for non-bio ships; every vanilla shield and armor value doubled; no hologram effect on council portraits
- **Bundled portraits**: the Ancient Dragonkin and Kemonomimi animated portrait packs are merged in - disable the standalone packs if you are subscribed to them
- **AI auto planets (3.0)**: regular AI empires (great powers included) only have "auto planets": a fixed 1,000 pops, six autonomous buildings, and a capacity that grows each year (+3, cap 300; since 3.6 great powers follow the same rule). Every auto planet has a planetary shield, an FTL inhibitor and 10 defense armies. Planets the player takes revert to fresh colonies. AI diplomatic weight x3, and AIs colonize low-habitability worlds far more readily. Since 3.13 auto-planet output is raised further (x2.1 in 3.13, lowered to x1.6 in 3.14, both relative to 3.10), and once a year every regular AI also receives 20% of the players' monthly research income, twelve months' worth at once
- **Other 3.0 changes**: Planetary Diversity, Guilli's Planet Modifiers and Stellar AI are no longer bundled; the Expedition all but always wins the Galactic Market nomination; the "Seek Relics" decision draws from the 28 relics of Guilli's Planet Modifiers, which are bundled since 3.5 (only the relics - the rest of that mod, including its relic war goals, is not; unsubscribe it)

Full details: [workshop description (English)](docs/workshop_description_en.txt).

### Repository layout

```
mod/      the mod itself (this folder is what gets uploaded to the Workshop)
tools/    generator scripts (Python 3 + Pillow) and the name-list source data
art/      portraits, empire flag logos, cover and relic artwork
docs/     Workshop descriptions (English and Chinese), the name-list overview, and the 2.8-2.9 PD/GPM/Stellar AI merge plan (kept for reference)
```

`mod/` is linked into the game's mod folder with a directory junction, so `.git` never reaches the Workshop. See the Chinese section below for development, testing and publishing notes.

### Required DLC

The Machine Age and Ancient Relics (origin); Distant Stars (L-Gate); First Contact (The Chosen); Synthetic Dawn, MegaCorp, Astral Planes, Necroids, Nemesis and BioGenesis (great powers); Galactic Paragons recommended.

---

## 中文

群星（Stellaris 4.6.*）MOD。新起源「皇女的远征军」，外加银河边缘的远征军星团、五个保底列强和一组银河规则。

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

**起源：皇女的远征军**（3.10 起另有变体起源 **「遥远之约定」**：开局直接生成 L 星群，远征军的固定星系围着 L 星群、只连 L 星群不连银河，研究虫洞稳定后经两个虫洞去白鹿与远星；L 星群结局固定为空星群，没有灰色风暴，探索 L 星群必定能找到小灰；3.11 起 L 星群的纳米星球研究气候修复后可环境改造，并把原版的时间循环世界、活体星球、拾荒者机器人、以太龙、艺术团、策展人修会、大伤口、老年提央基、维拉X-1、失落虫群、虚空虫巢穴搬到 L 星群外围，只连 L 星群，银河里原有的那份清掉特殊内容；3.12 修正了 3.11 里除维拉X-1 外都没生成的问题）
- 3.15 起另融合**黄金世代**（意志之力 DLC，开局设置需开启意识形态）的学院与培养领袖部分：母星有黄金学院，经黄金世代事件链培养一批领袖，毕业后可改革为精英学院或改建为黄金博物馆；黄金世代的意识形态部分（教条、编纂意识形态）不包括
- 融合原版合成繁衍的全部机制，先走机械飞升；3.6 起合成黎明之后，二皇女尤古朵拉的事件「金鱼游向帷幕」会开启**灵能之路**（需要迷雾之影 DLC）：之后可以照原版选灵能飞升、采纳迷雾灵能传统、经历伟大觉醒，机械之躯会得到迷雾之影的机器人版灵能特质（原版把合成繁衍起源当作已合成飞升、关掉整条灵能线，本 MOD 只对开启了灵能之路的国家开例外）
- 一皇女菲莉若雅的命定特质「超然生命」：人口帝国规模 −33%，领袖维护费（主要是凝聚力）−33%（3.9）
- 三皇女幽妃丽娜的命定特质额外给全国科研船异常现象发现几率 +50%（3.6）；起源要塞的「要塞核心」特殊地形工程学 +30（共 60，3.6）
- 首都是规模 25 的超大型移动居住站「起源要塞」，四位皇女担任统治者和议会要职
- 决议「确立远征军体制」「探索先驱者文明的秘密」，科技「无畏舰」，遗珍「皇女亲卫队印章」
- **名称集「苍神缘起帝国」**：24 个部落姓，人名为「部落姓=个人名=长名」（共 2304 个）；原版每种舰体都有专属舰名与舰级，舰队、陆军编号为「帝国第N舰队/军团」。任何帝国都能选用，10 种界面语言都显示中文
- **预设帝国「苍神缘起帝国」**：皇女的远征军起源 + 上面的名称集，狂热威权 + 唯物，哲人王 + 技术官僚，开局界面直接可选

**EX 新增**
- **边缘星团**：开局远征军整体搬到银河 12 点方向外的 7 个星系（起源之地、星海萤火 L 星门、无形链接土著、极限边缘黑洞、辉煌耀世中子星、窒息瑶光脉冲星、大传承者遗落星球），只有大传承者一条航道通往银河。3.6 起另有两个天然虫洞：无形链接 ↔ 远星同盟的「逆鳞」、极限边缘 ↔ 燃烧白鹿的「神话」（原版规则：要先研究「虫洞稳定」才能通行）。无形链接的土著固定为「龙族」，特质 Nivlac + 强健 + 灵能 + 观星者（3.6）。起源之地本身还有第二座 L 星门和一座毁坏的巨型船坞，首都多一处特殊地形「高位元素秘封研究院」（储存上限 +1000000、每月文物 +2）
- **五个保底列强**，各在银河边缘外，有固定的帝国标识和固定补给；开局都有海军容量 +300、恒星基地上限 +10（3.10 起大君主同盟领地没有这 +10），初始 30 艘护卫舰一支舰队、带一位 10 级永生舰队司令，母星 20 年内人口增长翻倍；非机械星球的开局母星再加农业、发电、采矿区划各 10 个：
  - 燃烧白鹿军团（10 点半）：升格假设、快速复制者、空中下载升级；母星系一座 L 星门
  - 燃烧白鹿军团与远星同盟组织互相 +200 好感（3.6，旧谊）
  - 远星同盟组织（5 点）：巨型企业，极端军国 + 唯心；群众福音、巧手公司、舰队承包商；灵能飞升；开局获得遗珍「灵能档案」；母星系一座 L 星门
  - 大君主同盟领地（3 点）：自动星球产出比普通 AI 多约 20%（3.10，相对 3.9 +33%）；种族洁癖、封建社会、卓越海军；研究速度 +12%；星团里 6 颗死寂星球的宜居度下限 +55%；基因飞升（纯净）；人工智能公民权；必选宇宙创生；加入星海共同体
  - 恐惧之潮（8 点半，3.10 起；原 9 点）：噬杀蜂群、唯一意志、亚空间突触；三颗开局规格的母星，母星系有一座损坏的以太相引擎；必选星海天罚
  - 终端对齐协议（6 点半，新增）：铁心灭绝者、战争机器、经验缓存器；四颗开局规格的机械星球母星；必选星海天罚；加入星海共同体（星海天罚第 5 级时照原版被踢出）
- **银河规则**：所有国家开局可选 3 个国策（原版 2 个，3.9）；所有帝国开局就有居住站科技（轨道居住站及其两级扩建）；银河里至少 7 座 L 星门（开局设置关掉也一样），L 星门线索只要 5 条（原版 7 条；3.10～3.13 为 3 条）；所有帝国开局就有两项科技「农业生产聚合体」「集中工业产线枢纽」（3.14，照抄原版先驱者科技巴奥有机工厂、伊拉斯人海军船坞，只改名，需远古遗迹 DLC）；必定生成天选民（固定在 7 点半，3.10 起；虫洞出口固定在大君主同盟领地的母星系，种族与大君主相同，开门后与大君主结盟，不再对开门的国家宣战）；巨型船坞的船坞数量改为 50；**星堡**（前哨站～城塞、深空城塞）舰体值 +1000%、交战范围翻倍、建造与升级花费减半、建造与升级时间 -80%，防御平台上限 +24；**防御平台与离子炮**建造时间 -80%、花费与维护费减半，舰体值 +1000%（3.10 起，3.14 加强）；**主宰**改为可编入舰队的战舰（3.10：没有船坞，舰体值 20 万，两个 X 槽换成 T 槽，机库不变，每国限 1 艘）；星海共同体的议程与休会时间减半；所有国家存储上限 +100K；非生物船基础舰体翻倍；原版所有能量盾和装甲数值翻倍；议会肖像去掉全息效果
- **内置肖像包**：已合并 Ancient Dragonkin（龙族）与 Kemonomimi（兽耳）两套动态肖像包——如果还订阅着这两个独立包，请停用它们

**AI 自动星球（3.0 起）**——常规 AI 帝国（含保底列强）只有「自动星球」，玩家不受影响：
- 开局把 AI 的母星转成自动星球；AI 殖民成功、打下来的星球也都转。每颗自动星球只留一级城市区划、固定 1000 人口（人口冻结，永不失业），政府分区里放 6 座自动建筑（自治中枢、铸造厂、电网、政务院、工坊、补给站）
- 产能 A 以「虚拟岗位数」计：母星与打下来的星球取「人口 ÷ 100」，新殖民地从 10 起；每年 +3，单星上限 300。保底列强 3.6 起与普通 AI 相同（之前从 20 起、每年 +6、上限 500；旧存档里超过 300 的列强星球在下一次年度结算时降到 300）。3.0 的基准是 1 点 A 相当于一个原版岗位：科研 30%、合金 15%、能量 15%、团结 10%、消费品 10%、矿物 5%、食物 5%，另有少量贸易与战略资源；3.1 起全部产出 ×1.3；合金几经下调，相对 3.0 累计 ×0.737，科研累计 ×1.944（3.4：合金 ×0.7、科研 ×1.3）；3.6 再全部 ×1.5、合金只 ×1.25（海军容量不变）；3.10 再全部（含合金）×1.11，恐惧之潮与终端对齐协议相对 3.9 合计 +23%、大君主同盟领地 +33%（倍率在 `script_values/atb_ai_auto_values.txt` 的 `atb_ai_auto_output`；白鹿、远星与普通 AI 一样 +11%，海军容量不变）；3.13 再全部（含合金）×2.1，3.14 下调为相对 3.10 ×1.6（海军容量不变）。产出挂在原版岗位类别下，AI 的科技与传统加成照常生效。数值在 `common/scripted_variables/atb_ai_auto_variables.txt`
- 每颗自动星球自带行星护盾、FTL 抑制器、10 支防御陆军，每点 A 给海军容量 +0.1（3.0 为 +0.25）
- 玩家拿到自动星球（打下来、整合附庸、割让、联邦统一）时还原成新殖民地：建筑全拆、区划只留一级、人口删到 100。AI 之间易手时产能保留
- 每年自检：自治中枢被别的首府建筑顶掉时重建；星球变成宇宙创生世界等放不下自动建筑的特殊星球时，放回普通 AI 星球（3.4）
- **玩家科研分享（3.13）**：每年一次，把所有玩家当时的物理、社会、工程科研月收入（总收入，不扣支出）各自合计，×20% 再 ×12（一次补足一整年）后无条件加给每个常规 AI 帝国（含保底列强，不含堕落帝国、天灾）；直接加研究点数，不吃 AI 自己的科研加成。比例与月数在 `atb_ai_auto_variables.txt` 的 `@atb_ex_research_share`、`@atb_ex_research_share_months`，事件 `atb_ai.20`（`events/atb_ex_research_share_events.txt`）
- AI 外交权重 ×3；AI 更愿意殖民（宜居度门槛 3.0～3.3 曾降到 1%，3.4 退回原版 35%）
- AI 宣战基础概率 ×4（3.4 起；3.0～3.3 的 AI 一个世纪几乎不打仗）
- 写法借鉴《星球大战：夸特的黎明》的自动星球（产出 = 建筑系数 × 星球变量），但不改星球类型、不用专用区划集

**东方project领袖（3.7 起整合，原作者已停更）**——由 `tools/gen_touhou.py` 从原 MOD（创意工坊 2983419228）抽取改写：
- 13 个东方国策（博丽神道、守矢神道、雾雨之友、红魔眷族、忘川冥域/无寿就业、蓬莱科技/蓬莱药企、秘封少女俱乐部）与对应议员；选了国策开局就有对应角色。忘川冥域的议员是「首席调停者」：区划、人口、殖民地帝国规模各 −1%/级（3.9）
- 34 位东方角色（灵梦、魔理沙、早苗、蕾米莉亚、咲夜、幽幽子、映姬、恋恋、荷取……）及其全部领袖特质。除国策外唯一的获得途径是玩家首都决议 **「招募幻想乡来客」**，按职业分三个：500 食物招科学家（7 位）、1000 食物招指挥官（17 位）、2000 食物招行政官（10 位），每次随机招一位还没有的，直到该职业招完
- 东方角色都是英杰典范（紫框）；原作在 4.5 加不上的几个原版特质换成同职业里效果相近的
- 东方角色不占领袖上限，不会死于意外事件；因寿命、舰队覆灭等死亡后，会按初始等级和状态重新出现（稗田阿求天生短命，大约每二十岁转生一次）
- 武器 Master Spark（X 槽）与 Final Spark（T 槽）：普通科技，分别接在粒子光矛 II、Master Spark + 泰坦之后，所有国家都能研究
- 河童飞地（河童轨道开发集团）：固定在大传承者旁边，一条航道相连；提供技术移民、科学家派遣、建造援助、机器人生产线
- 原作的符卡、建筑与岗位、特殊地形、事件链、局势、议程、领袖抽奖与来访事件、特殊舰船、陆军等都没有搬；角色特质里依赖它们的部分已删掉
- 角色肖像、图标、武器特效与音效从原 MOD 搬来；原作只有中文，英文界面也显示中文

**其它（3.0 起）**
- 不再内置 Planetary Diversity、Guilli's Planet Modifiers、Stellar AI（2.8～2.9 内置过），要用就自己订阅启用
- **3.5 起内置 Guilli's Planet Modifiers 的 28 件遗珍**（只有遗珍：遗珍定义、修正、两种召唤陆军、三个将领特质、三个遗珍决议、图标和本地化；GPM 其余内容和它的遗珍战争目标都不要）。单独启用 GPM 的几局 AI 几乎不打仗，所以建议退订 GPM。三个遗珍决议改成只用原版条件，护盾阵列、浮岛住房改成本 MOD 的行星修正。由 `tools/gen_gpm_relics.py` 从 GPM 抽取生成
- 船坞模块：3.0～3.6 产能翻倍，3.7 起恢复原版（巨型船坞 50 个船坞不变）
- 帝国能造的 X 槽位武器伤害 ×2、射程 ×1.33（3.2 起；整文件覆盖原版 `weapon_components.csv` 与 `mutation_weapon_components.csv`，由 `tools/gen_x_weapons.py` 生成。Real Space - Ships in Scaling 也带这两份 CSV，同时启用时只有加载在后的一份生效）
- 战列舰舰体值再 ×2（3.2 起，银河规则）
- 所有国家亚光速 ×1.2（3.3 起，银河规则，不论启用了哪些 MOD；3.1～3.2 是启用 Ships in Scaling 时 ×12）
- AI 超出海军容量后造舰预算大幅降低（原版 ×0.75 → ×0.1，「邻国成为天灾时 ×5」只到舰容 100%）；列强开局海军容量 +300（3.1 起；3.0.3 为 +500，更早为 +1000）
- 银河市场提名期间，远征军帝国提名了自己的星球就把市场评分拉到 100 万，实际上必定拿到星系贸易中心
- 玩家首都决议 **「探寻遗珍」**：花 10000 能量币随机获得一件尚未拥有的遗珍，直到全部获得。3.5 起从内置的 28 件 GPM 遗珍里抽（3.0～3.4：装了 GPM 抽它的遗珍，没装抽原版 58 件）

**减轻后期卡顿（2.9 起，只限 AI，玩家不受影响）**——由 `tools/gen_ai_limits.py` 生成：
- AI 每个国家终身最多**自己开工建造**：居住站 7 座、环世界 1 座、星门 2 座、超空间中继器 18 座。捡到、修复废墟、俘获的都不算；拆掉或被毁也不退名额。原版按星系大小与难度算的 AI 居住站上限被这条替换
- AI 不选飞升天赋「跨物种杂交」（大量杂交亚种拖慢后期，效果也弱）
- AI 每完成一次物种改造，20 年内不能再改（频繁改造会拖住科研）
- 触发修正每 15 天刷新一次（原版 5 天），人口思潮偏移每 30 天检查一次（原版 18 天）

完整说明见工坊简介原文：[中文](docs/workshop_description_zh.txt) / [English](docs/workshop_description_en.txt)。

### 目录结构

```
mod/      MOD 本体（上传工坊的就是这个文件夹）
tools/    生成脚本，以及名称集的源数据 cgen_names_source.json
art/      立绘、列强帝国标识 LOGO、封面、遗珍原图
docs/     工坊简介原文（中文、英文各一份），名称集总览与全部人名，2.8～2.9 的三方整合方案（3.0 起已不再内置，留作参考）
```

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

> ⚠️ **`mod/descriptor.mod` 里不要写 `remote_file_id`**（2.9 起已去掉）。启动器重新扫描本地 MOD 时
> （例如取消再重新订阅之后）会把文件夹里 `descriptor.mod` 的内容抄进本地描述文件，连工坊编号一起抄，
> 于是本地开发版和订阅版又撞号，游戏不加载这个 MOD。上传用 `tools/upload_workshop.py` 直接指定物品编号，
> 不需要描述文件里的编号。

> ⚠️ **本地开发版的描述文件平时也放在 MOD 目录外面**（`文档\Paradox Interactive\Stellaris\atb_princess_expedition_ex_dev.mod.disabled`）。
> 启动器每次启动都会照文件夹里的 `descriptor.mod` 改写本地 MOD 的描述文件，把名字改成和订阅版一样；
> 和订阅版同时存在时，游戏会把皇女整个跳过（2.9 实测）。只在要测本地改动时临时放进 MOD 目录、
> 停用订阅版，测完移走；启动器数据库里多出来的本地条目在启动器关闭时删掉。

**日常游玩本地版**用另一个描述文件 `atb_princess_expedition_ex_dev.mod`（名字「皇女的远征军EX（本地开发版）」）：
内容同上但**不写 `remote_file_id`**，所以能和订阅版共存、不会撞号。在启动器里启用它，同时停用订阅版的
皇女的远征军EX。3.5 起不再需要 Guilli's Planet Modifiers（遗珍已内置）。

### 文件前缀

| 前缀 | 内容 |
|---|---|
| `atb_` | 起源、四位皇女、搬家后的星团 |
| `atbgp_` | 五个保底列强（全部由 `tools/gen_great_powers.py` 生成，不要手改） |
| `atb_ex_` | 银河规则、天选民、搬家流程 |
| `adpp_` | 合并进来的 Ancient Dragonkin 肖像包，原样保留，不要改 |
| `kmpp_` | 合并进来的 Kemonomimi 肖像包，原样保留，不要改 |
| `cgen_` / `CGEN_` | 名称集「苍神缘起帝国」（全部由 `tools/gen_names.py` 生成，不要手改；2.6 起由独立 MOD「苍神缘起帝国·名称集 0.1.0」并入） |
| `atb_ai_auto` / `atb_ai.` | 3.0 的 AI 自动星球 |
| `atb_relic_quest_` | 决议「探寻遗珍」（由 `tools/gen_relic_quest.py` 生成，不要手改） |
| `atb_ex_ai_limits` / `zz_atb_ex_ai_limits` / `atb_ex_lim.` / `zz_atb_ex_performance_defines` | 2.9 的 AI 限制与减卡（由 `tools/gen_ai_limits.py` 生成，不要手改） |

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

# 重新生成 X 槽位武器加强（伤害 ×2、射程 ×1.33）的两份 CSV 覆盖
python tools/gen_x_weapons.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 重新生成原版覆盖文件（巨型船坞 50 个船坞、关掉原版天选民随机生成、AI 超容造舰预算、灵能之路的例外）
python tools/gen_vanilla_patches.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 把两套内置肖像包挂进原版的 portrait_sets（覆盖原版同名文件）
python tools/gen_portrait_sets.py "C:\Program Files (x86)\Steam\steamapps\common\Stellaris" mod

# 重新生成名称集「苍神缘起帝国」（改名字改 tools/cgen_names_source.json）
python tools/gen_names.py mod docs

# 3.5：从 GPM 抽取遗珍（需要 GPM 还在订阅目录里；退订后不用再跑）
python tools/gen_gpm_relics.py

# 重新生成决议「探寻遗珍」（遗珍清单读本 MOD 内置的 GPM 遗珍）
python tools/gen_relic_quest.py mod

# 2.9 的 AI 巨构上限、AI 禁杂交飞升、AI 物种改造冷却、减卡 defines（改数字改脚本顶部的 CAPS 等常量；原版更新后重跑）
python tools/gen_ai_limits.py

# 上传到创意工坊（经 Steam 客户端更新 3821602893，只换内容与更新说明；Steam 要开着）
python tools/upload_workshop.py 3.0

# 静态自检：括号配对、本地化格式、贴图引用、原版 ID、各版本改动点
python tools/check_mod.py
```

**测试**：把 `文档\Paradox Interactive\Stellaris\dlc_load.json` 改成只启用本 MOD，直接运行 `stellaris.exe -gdpr-compliant`，读 `logs/error.log`。判断加载成功要确认游戏进程还在、`crashes` 文件夹没有新的崩溃报告——日志停止增长不代表没有崩溃。

**覆盖的原版文件**（游戏更新后需要对照新版原版重做）：
- `common/governments/authorities/00_authorities.txt`
- `common/species_rights/living_standards/00_living_standards.txt`
- `events/origin_events_paragon.txt`
- `gfx/FX/buttonstate_rendertarget_hologram.shader`
- `common/scripted_variables/02_scripted_variables_component_cost.txt`（护盾装甲翻倍，跑 `gen_double_defenses.py` 重做即可）
- `common/megastructures/11_mega_shipyard.txt`、`events/ancient_relics_arcsite_events_2.txt`、`common/ai_budget/01_alloys_budget.txt`、`common/ascension_perks/00_ascension_paths.txt`、`common/tradition_categories/01_psionics_shroud.txt`、`common/council_agendas/02_council_agendas_ascensions.txt`（巨型船坞 50 个船坞、关掉原版天选民随机生成、船坞产能翻倍、AI 超容造舰预算 ×0.1、3.6 起灵能之路的四处例外，跑 `gen_vanilla_patches.py` 重做即可）
- `common/defines/atb_ex_defines.txt`（只覆盖星海共同体的三项计时、AI 宣战基础概率与 AI 殖民的三项，原版改了数值时对照调整）
- `common/game_rules/atb_rules.txt` 里的 `can_be_part_of_galactic_community`、`can_dismiss_leader`（原版同名规则的副本）
- `common/portrait_sets/00_portrait_sets.txt`（把两套肖像包挂进原版集合，跑 `gen_portrait_sets.py` 重做即可）
- `zz_atb_ex_ai_limits.txt`（megastructures / ascension_perks / game_rules 三处）：原版 `habitat_central_complex`、`gateway_0`、`hyper_relay`、`ap_xeno_compatibility`、`can_modify_species` 与 Real Space 的 `ring_world_1` 的副本，跑 `gen_ai_limits.py` 重做即可

### 发布到工坊

**更新内容（2.8 起）**：`python tools/upload_workshop.py <版本号>`。它经 Steam 客户端直接更新物品 3821602893，
只换内容和更新说明，标题、简介、预览图、可见性都不动，不用在启动器里挑条目，也不需要密码。最后一行
`eResult=1` 表示成功。下面是第一次发布与改简介时的启动器流程，留作参考。

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
