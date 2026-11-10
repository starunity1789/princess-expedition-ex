# 开发期分析脚本（排查用，不参与构建）

| 脚本 | 用途 | 用法 |
|---|---|---|
| `planets.py` | 解析存档 gamestate，统计星球数、带 GPM 修正的比例、按星球类型分组、GPM 全局旗标 | 先 `unzip xxx.sav -d 某目录`，再 `python planets.py 现在/gamestate 对照1/gamestate 对照2/gamestate` |
| `moddiff.py` | 两份存档按 GPM 修正所在文件对比每千颗星球的数量，列出完全消失的修正 | `python moddiff.py 现在/gamestate 对照/gamestate ...`（需与 planets.py 同目录） |
| `logdiff.py` | 两份 error.log 去掉时间戳/行号后对比，列出只在第二份出现的错误 | `python logdiff.py 基线.log 合并版.log` |
| `vanilla_gaps.py` | 上游覆盖的原版文件里，原版 4.5.3 有、上游版没有的顶层定义 | `python vanilla_gaps.py`（路径写死在脚本里） |

存档与日志都在 `文档\Paradox Interactive\Stellaris\save games\` 与 `logs\`。
