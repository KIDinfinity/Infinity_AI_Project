# plan_guitar_rumbling — 「The Rumbling」电吉他 4 轨合奏学习计划

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
