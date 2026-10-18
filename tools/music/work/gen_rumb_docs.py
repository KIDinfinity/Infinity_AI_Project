"""Generate root/phase/week docs for plan_guitar_rumbling (after day PLANs are generated)."""
import os
from gen_rumb_plans import DAYS, PHASE_OF, PHASE_TITLE, MILESTONE, TRACK_NAME, OUT, META

WEEK_THEME = {
    1: '基础入门：持琴 / 拨弦 / 爬格 / 强力和弦 + Solo A 认音',
    2: 'Solo A 前半（m1-6）+ Verse A 强力和弦认音',
    3: 'Solo A 后半（m7-12）并串成完整 Solo A',
    4: 'Verse A Rhythm1（m13-24）+ Solo A 复练',
    5: 'Verse A Rhythm1 收尾（m25-34）→ M1 验收 Solo A',
    6: 'Solo B（m50-58）+ Chorus Rhythm1 开头',
    7: 'Chorus Rhythm1（m35-50）完整 + Solo B 复练',
    8: 'Solo C（m77-93）→ M2 验收 Solo 轨旋律',
    9: 'Verse B Rhythm1（m59-74）完整',
    10: 'Chorus Rhythm2（m105-124）完整',
    11: 'Rhythm 双轨复练打磨 → M3 验收',
    12: 'Guitar3 Clean（m97-108）→ M4 验收',
    13: 'Solo D（m125-132）+ Solo 轨全曲结构串联',
    14: '全轨提速到目标速度（145bpm）',
    15: '跟伴奏/节拍器合奏 + 表现力打磨',
    16: '四轨完整录音 → M5 验收成品',
}

PHASE_GOAL = {
    1: '打好吉他基本功（姿势/拨弦/按弦/强力和弦），并把 Solo A 主音（m1-12）完整弹下，建立「慢就是快」的练琴节奏。',
    2: '分轨攻克全曲：Solo 轨全旋律（Solo A/B/C）+ 节奏双轨（Rhythm1/2）的强力和弦与闷音，逐轨拿下并串段。',
    3: '合奏成型：补完 Solo D 与 Guitar3 Clean，全轨提速到原速 145bpm，跟伴奏合奏并录制成品。',
}

PHASE_EXIT = {
    1: 'M1（第 5 周末）：Solo A 主音 m1-12 慢速完整、不断不错。',
    2: 'M2/M3/M4：Solo 轨全旋律、Rhythm1+2 全曲节奏、Guitar3 Clean 各自完整弹下。',
    3: 'M5（第 16 周末）：四轨均可完整弹，选主轨录制成品。',
}


def week_table(week):
    rows = []
    for d in DAYS:
        if d['week'] != week:
            continue
        i = d['dayno'] % 5
        idx = (i - 1) if i else 4
        tr = TRACK_NAME[d['track']] if d['track'] else '基本功'
        rows.append(f"| Day{d['dayno']:02d} | {d['date']} | {d['title']} |")
    return '\n'.join(rows)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)


def main():
    # root README
    readme = f'''# plan_guitar_rumbling — 「The Rumbling」电吉他 4 轨合奏学习计划

- **曲目**：The Rumbling（SiM / 进击的巨人 Final Season OP2）
- **编曲**：Arranged by KIKAHO
- **乐器**：电吉他（标准调弦 EADGBE）
- **起点水平**：零基础
- **每日投入**：60 分钟
- **每周练习**：5 天（周一至周五）
- **总周期**：16 周（约 4 个月）
- **起始日期**：2026-10-19（周一）
- **目标**：能完整演奏 The Rumbling 四轨中的任意声部，并录制成品

## 谱面来源

- 总谱：`draft/rumbling/rumb_stand.gp5`（Guitar Pro 5，4 轨，132 小节，145 BPM，C Major）
- 分谱 PDF（对应轨道）：
  | 文件 | 轨道 |
  | --- | --- |
  | `rumb_stand1.pdf`（2 页） | Guitar 3 (Clean) |
  | `rumb_stand2.pdf`（5 页） | Rhythm Guitar 1 |
  | `rumb_stand3.pdf`（3 页） | Rhythm Guitar 2 |
  | `rumb_stand4.pdf`（5 页） | Solo |

## 歌曲结构

| 段落 | 小节 | 活跃声部 |
| --- | --- | --- |
| Solo A | m1-12 | Solo |
| Verse A | m13-34 | Rhythm1 |
| Chorus | m35-50 | Rhythm1 + Rhythm2 |
| Solo B | m51-58 | Solo |
| Verse B | m59-74 | Rhythm1 |
| Solo C | m77-93 | Solo |
| Guitar3 Clean | m97-108 | Guitar3 |
| Chorus | m109-124 | Rhythm1 + Rhythm2 |
| Solo D | m125-132 | Solo |

## 阶段总览

| Phase | 周次 | 日期范围 | 主题 |
| --- | --- | --- | --- |
| Phase 01 | Week 01–05 | 10-19 → 11-20 | 基础入门 + Solo A 主音 |
| Phase 02 | Week 06–11 | 11-23 → 01-01 | 分轨攻克全曲（Solo / Rhythm1 / Rhythm2） |
| Phase 03 | Week 12–16 | 01-04 → 02-05 | 合奏 + 提速 + 打磨成型 |

## 目录结构

```
plan_guitar_rumbling/
├── README.md              ← 本文件
├── TARGET.md              ← 目标蓝图（里程碑）
├── GENERATED_WITH.md      ← 生成记录
├── phase_01/              ← 基础入门 + Solo A 主音（W1-5）
│   ├── README.md
│   └── week_01/ … week_05/
│       ├── README.md
│       ├── TASKS.md
│       └── dayNN_DATE/
│           ├── PLAN.md          ← 当天计划（含真实 tab 谱面）
│           ├── sheet.gp5        ← 当天专属分谱（Guitar Pro 5）
│           └── sheet.pdf        ← 当天专属分谱（五线谱+六线谱 PDF）
├── phase_02/              ← 分轨攻克全曲（W6-11）
│   └── week_06/ … week_11/
└── phase_03/              ← 合奏 + 提速 + 打磨（W12-16）
    └── week_12/ … week_16/
```

## 每日谱面

每个 `dayNN_DATE/PLAN.md` 的「第 9 节」内嵌当日小节的 ASCII 六线谱（16 分音符分辨率，直接从 gp5 提取渲染）。
同时每个曲目 day 都配有独立分谱文件（与 PLAN.md 同级）：
- `dayNN_DATE/sheet.gp5` — 从总谱切出的单轨当日段落（Guitar Pro 5），可用 Guitar Pro / TuxGuitar / MuseScore 打开、调速、播放
- `dayNN_DATE/sheet.pdf` — 同段落的五线谱+六线谱成品（MuseScore 渲染）

对照 PDF 分谱或总谱核对时，以 `draft/rumbling/` 下的 gp5/PDF 为准。
'''
    write(f'{OUT}/README.md', readme)

    # TARGET.md
    target = f'''# TARGET — 「The Rumbling」目标蓝图

## 最终目标（16 周后）

- ✅ 能不看谱（或仅作参考）完整演奏 The Rumbling 四轨中的任意声部
- ✅ 右手拨弦 / 强力和弦闷音 / 分解和弦节奏稳定
- ✅ 主音 Solo 旋律音准、节奏、音色干净
- ✅ 四轨中至少选一轨录制完整成品（音频/视频）

## 里程碑

| 里程碑 | 时间 | 验收标准 |
| --- | --- | --- |
| M1 | Week 05 末 (11-20) | Solo A 主音（m1-12）慢速完整、不断不错 |
| M2 | Week 08 末 (12-11) | Solo 轨全曲旋律（Solo A/B/C）完整弹下 |
| M3 | Week 11 末 (01-01) | Rhythm1 + Rhythm2 全曲强力和弦节奏（含闷音）完整弹下 |
| M4 | Week 12 末 (01-08) | Guitar3 Clean 分解全段（m97-108）完整弹下 |
| M5 | Week 16 末 (02-05) | 四轨均可完整弹，选主轨录制成品 |

## 每日练习结构（60 分钟）

| 时间段 | 时长 | 内容 |
| --- | --- | --- |
| 热身 | 5 min | 手腕/手指放松 + 空弦慢拨 |
| 主练 | 35 min | 当日核心任务（分段精练） |
| 复习 | 15 min | 复习已学段落，保持手感 |
| 总结 | 5 min | 记录进度、难点、明日重点 |

## 核心原则

1. **慢就是快**：所有新段落从极慢速（60bpm）开始，准确优先于速度
2. **分段攻克**：每天只聚焦 2-4 小节的精练，不贪多
3. **右手先行**：节奏不稳时先单独练右手（拨弦/闷音），再合左手
4. **录音自检**：每周至少录音一次，客观评估进度
5. **锚点一致**：每天都能回答「今天练的与最终合奏目标的关系」
'''
    write(f'{OUT}/TARGET.md', target)

    # GENERATED_WITH.md
    gw = f'''# GENERATED_WITH — 本 plan 的生成与落地记录

> 记录「The Rumbling 电吉他 4 轨合奏学习计划」从生成到落地用了哪些东西，方便复现或迁移到下一首曲子。

## 1. 规划方式
- 驱动 prompt：`prompt/target_plan_prompt.md`
- 拆解原则：目标分细化（5 里程碑 M1–M5）、循序渐进（基本功 → 分轨 → 合奏 → 提速 → 录音）、每天只做一件事、每个 day 写清与最终目标的关系
- 结构：3 阶段 × 16 周 × 5 天 = 80 天

## 2. 用到的 prompt / 文档
- `prompt/target_plan_prompt.md` — 通用「给 target 定 plan」的生成规范
- `draft/rumbling/rumb_stand_summary.md` — 谱面解析说明（轨道/调弦/速度）
- `draft/rumbling/rumb_stand.gp5` — 总谱源文件（4 轨）
- `draft/rumbling/rumb_stand1~4.pdf` — 分谱（Guitar3 / Rhythm1 / Rhythm2 / Solo）

## 3. 用到的工具 / 脚本
| 工具/脚本 | 作用 | 状态 |
| --- | --- | --- |
| `tools/music/work/rumb_extract.py` | PyGuitarPro 解析 gp5 → `rumb_data.json`（小节/音符/时值/演奏技巧标记/日历） | 已用 |
| `tools/music/work/gen_rumb_plans.py` | 读取 rumb_data.json → 渲染 tab + 逐小节精练清单（音符/和弦/把位/技巧）+ 生成 80 个 PLAN.md | 已用 |
| `tools/music/work/gen_rumb_docs.py` | 生成 README/TARGET/GENERATED_WITH/phase/week 文档 | 已用 |
| `tools/music/work/gen_rumb_sheets.py` | 切分总谱 → 每个 day 的 `sheet/sheet.gp5`（+ `--pdf` 转 `sheet.pdf`） | 已用 |
| `tools/music/work/dump_rumb.py` | 采样打印各轨小节音符（排查用） | 已用 |

## 4. 用到的 agent / skill
- 无（规划与脚本编写由主对话完成）

## 5. 外部依赖 / 环境
- Python + `PyGuitarPro`（`uv run --with PyGuitarPro`）— 解析 + 写出 Guitar Pro 5 文件
- MuseScore 4（`mscore` CLI，`/opt/homebrew/bin/mscore`）— gp5 → PDF 渲染
- 标准库 json / os / datetime / subprocess — 数据结构、日历与外部命令调用

## 6. 关键产物
- `tools/music/work/rumb_data.json` — 全曲结构化数据（4 轨逐小节音符+时值）
- `tools/music/work/rumb_extract.py` — 数据提取脚本（可复现）
- `tools/music/work/gen_rumb_plans.py` — 计划生成脚本（可复现/可改 DAYMAP 后重跑）
- `tools/music/work/gen_rumb_sheets.py` — 分谱切分脚本（可复现/`--pdf` 切换）
- 80 个 `dayNN_DATE/PLAN.md` — 每天详细计划（含真实 tab 谱面）
- 76 个 `dayNN_DATE/sheet.gp5` + `sheet.pdf` — 每天专属分谱（基本功日无谱面）

## 7. 已知瑕疵
- 每个 PLAN 的「本日精练清单」已自动标注推弦/击弦/滑音/闷音/揉弦/延音/泛音等技巧记号，但「第 9 节」的 ASCII tab 本身仅按 16 分音符分辨率对齐、不含技巧记号，练到对应小节仍建议对照 gp5/PDF 原谱核对。
- 时值取整到 16 分格，三连音等细分节奏在 tab 中会被近似对齐，以原谱为准。
'''
    write(f'{OUT}/GENERATED_WITH.md', gw)

    # phase README + week README/TASKS
    for phase in (1, 2, 3):
        weeks = [w for w in range(1, 17) if PHASE_OF[w] == phase]
        wstart, wend = weeks[0], weeks[-1]
        ph = f'''# {PHASE_TITLE[phase]}

## 阶段目标

{PHASE_GOAL[phase]}

## 周次概览

| Week | 主题 |
| --- | --- |
''' + '\n'.join(f'| {w:02d} | {WEEK_THEME[w]} |' for w in weeks) + f'''

## 里程碑 / 出阶段条件

{PHASE_EXIT[phase]}

## 进出阶段判断

- 进入条件：上一阶段里程碑已勾掉（Phase 1 无前置）。
- 出阶段条件：本阶段对应里程碑全部可勾掉。
'''
        write(f'{OUT}/phase_{phase:02d}/README.md', ph)

        for w in weeks:
            days = [d for d in DAYS if d['week'] == w]
            first = days[0]['date']
            last = days[-1]['date']
            wr = f'''# Week {w:02d} · {WEEK_THEME[w]}（Phase {phase} · {first} → {last}）
'''
            write(f'{OUT}/phase_{phase:02d}/week_{w:02d}/README.md', wr)

            tasks = f'''# Week {w:02d} · TASKS

## 本周目标

{WEEK_THEME[w]}

## Day 概览

| Day | 日期 | 任务 |
| --- | --- | --- |
{week_table(w)}

## 本周里程碑

{MILESTONE[w][0]} — {MILESTONE[w][1]}
'''
            write(f'{OUT}/phase_{phase:02d}/week_{w:02d}/TASKS.md', tasks)

    print('docs generated')


if __name__ == '__main__':
    main()
