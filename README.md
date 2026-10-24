# 皇女的远征军EX

群星（Stellaris 4.5.*）MOD。新起源「皇女的远征军」，外加银河边缘的远征军星团、三个保底列强和一组银河规则。

- Steam 创意工坊：[皇女的远征军EX](https://steamcommunity.com/sharedfiles/filedetails/?id=3821602893)
- 世界观：[观星者计划 / The Stargazer Project](https://github.com/starunity1789/StargazerPR)

## 故事背景

四位皇女来自观星者计划中星间林地凛冬大陆的**苍神缘起帝国**（CNP8）。帝国由星间林地第一位真正意义上的永生者——黯王统治，实行哲人王威权民主制，是精灵-苍神缘起-凛冬合众国-河童重工四国同盟中的主导国家。

本 MOD 的故事发生在**黯王失踪之前**：帝国独自突破了高等科技，但母星依旧四分五裂。皇帝留守母星，四位皇女驾驶移动要塞「起源要塞」远赴群星，为帝国开辟新的根基。随行的殖民者水土不服、身患绝症，再也无法繁衍，皇女们只能带领族人走上合成繁衍之路。

EX 新增的三个列强也与帝国有关：燃烧白鹿军团是帝国盟友精灵族制造的机器人军团，远星同盟组织由帝国母星上的其他精英与国家组成，大君主同盟领地则是一个遍布宇宙的高等封建文明的乡村领地。

## 四位皇女

四位角色的内在设定、外貌与全部细节由作者于 2022 年构想完成；立绘根据作者的设计由 AI 绘制。

| | 角色 | 职位 | 设计来源 |
|---|---|---|---|
| 第一皇女 | 菲莉若雅 | 统治者 · 指挥官 | 中国传统服饰，加以现代改良 |
| 第二皇女 | 尤古朵拉 | 国防部长 · 指挥官 | 东亚三国文化的融合，脚下穿的是木屐 |
| 第三皇女 | 幽妃丽娜 | 科学部长 · 科学家 | 当代中国流行的修真体系服饰 |
| 第四皇女 | 安泰熙雅 | 国务卿 · 行政官 | 西方风格 |

## 主要内容

**起源：皇女的远征军**
- 融合原版合成繁衍的全部机制，只能走机械飞升
- 首都是规模 25 的超大型移动居住站「起源要塞」，四位皇女担任统治者和议会要职
- 决议「确立远征军体制」「探索先驱者文明的秘密」，科技「无畏舰」，遗珍「皇女亲卫队印章」

**EX 新增**
- **边缘星团**：开局远征军整体搬到银河 2 点钟方向外的 7 个星系（起源之地、星海萤火 L 星门、无形链接土著、极限边缘黑洞、辉煌耀世中子星、窒息瑶光脉冲星、大传承者遗落星球），只有大传承者一条航道通往银河
- **三个保底列强**：燃烧白鹿军团（11 点）、远星同盟组织（5 点）、大君主同盟领地（9 点），各在银河边缘外有自己的星团和固定补给
- **银河规则**：必定生成天选民和凯德斯（瓦格罗之子嗣）的坠毁点；所有国家存储上限 +100K；非生物船基础舰体翻倍；议会肖像去掉全息效果

完整说明见 [docs/workshop_description.txt](docs/workshop_description.txt)（即工坊简介原文）。

## 目录结构

```
mod/      MOD 本体（上传工坊的就是这个文件夹）
tools/    生成脚本
art/      立绘、封面、遗珍原图
docs/     工坊简介原文
```

`mod/` 通过目录联接（junction）挂到游戏的 MOD 目录：

```
文档\Paradox Interactive\Stellaris\mod\atb_princess_expedition_ex  →  本仓库\mod
```

游戏和启动器看到的路径不变；`.git` 在 `mod/` 之外，不会被传到工坊。

## 文件前缀

| 前缀 | 内容 |
|---|---|
| `atb_` | 起源、四位皇女、搬家后的星团 |
| `atbgp_` | 三个保底列强（全部由 `tools/gen_great_powers.py` 生成，不要手改） |
| `atb_ex_` | 银河规则、天选民、凯德斯、搬家流程 |

## 开发

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

## 发布到工坊

1. 从 Steam 启动群星（单游戏启动器），进入「Mod 库 → 上传 MOD」，选「皇女的远征军EX」，上传到「Steam 创意工坊」。Mod ID 应自动显示 3821602893。
2. 上传前把 `docs/workshop_description.txt` 的内容贴进描述栏——上传会用这一栏覆盖工坊简介。简介上限约 8000 字节（按 UTF-8 计算）。
3. 如果提示「已存在具有相同远程 ID 的本地 Mod」，是启动器数据库 `launcher-v2.sqlite` 里别的本地条目还登记着这个编号：关掉启动器，把那些条目的 `remoteSteamId` 清空即可。
4. 更新后 Steam 会自动做内容检查，期间物品暂时隐藏，通过后自动恢复。

## 需要的 DLC

机械纪元、远古遗珍（起源必需）；远星（L 星门）；首次接触（天选民）；合成黎明、巨企、死灵物种包、复仇女神（三个列强）；银河英杰（推荐）。
