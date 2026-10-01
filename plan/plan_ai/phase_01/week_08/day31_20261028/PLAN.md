# Day 31 · 2026-10-28 · Week 08 Task 2：Demo 录制 + 技术复盘 8 问

## 0. 今天只做一件事

录一段 90 秒 Demo（导出 <10MB 的 GIF 放进 README），并用评测报告里的真实数字写完 `docs/portfolio/p1.md`（总计划 §4.8 的 8 问 + 3 分钟讲稿）。

不碰：剪辑配乐 / 字幕特效、视频网站发布、技术博客长文（W16）、任何功能修改（发现 bug 只记录，除非阻断 Demo）。

## 1. 资产锚点

- 构建模块：M13.2 项目写作：P1 技术复盘（Demo + 8 问）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.5 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`docs/assets/demo.gif`（**MB，5 个镜头）；`p1.md` 8 问每问有数字与证据链接；3 分钟讲稿实测时长 \_\_**
- 今日 AI 实际应用：把「为什么用 RAG、怎么降幻觉、怎么评估检索、怎么控成本」这些 AI 工程问题，用自己系统的数据作答——这是 AI 岗位面试最核心的考察方式

## 2. 起点（前置确认）

- 已有：Day30 的 README / 架构 / ADR；W5 评测报告与 badcases；本地 `make up` 或云端可用。
- 需确认：

```bash
cd ~/lab/workpilot && make up && make ps
ls eval/reports/ eval/badcases/
grep -c "^## " eval/badcases/badcases.md          # badcase 条数（验收要求 ≥ 10）
brew list --cask kap 2>/dev/null || echo "可选：brew install --cask kap（直接导出 GIF）"
which ffmpeg || echo "可选：brew install ffmpeg（mov → gif）"
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `docs/assets/demo.gif` < 10MB，时长 ≤ 90 秒，包含 5 个镜头：上传 → 库内提问看引用 → 库外提问看拒答 → 👎 反馈 → 评测报告
- [ ] README 中 GIF 占位已替换，VS Code 预览可播放
- [ ] `docs/portfolio/p1.md` 8 问全部完成，每问含「结论 + 数字 / 证据链接」
- [ ] p1.md 含 3 分钟讲稿；计时朗读一次，时长 2:30–3:15
- [ ] Demo 画面中无公司信息、无真实同事姓名、无本机用户名路径、无 API key
- [ ] 已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                        |
| ------- | ------ | ----------------------------------------------------------- |
| 0–15    | P0     | 准备 Demo 环境：清空无关会话、选定问题、浏览器窗口 1280×800 |
| 15–40   | P0     | 彩排 1 次 → 录制（最多 3 次，选最好一条）→ 导出 GIF         |
| 40–95   | P0     | `p1.md` 8 问                                                |
| 95–110  | P0     | 3 分钟讲稿 + 计时朗读 1 次                                  |
| 110–120 | P0     | 替换 README 占位 + 提交                                     |

时间不足时最低保留：8 问写完（面试用得最多）；GIF 降级为 3 张截图（引用 / 拒答 / 评测）。

## 5. 今日学习（只学完成任务必须的）

- Demo 原则：一个镜头只证明一件事；先展示结果再展示过程；画面上要能读到关键文字（引用标题、拒答提示、指标数字）。
- GIF 体积 ≈ 分辨率 × 帧率 × 时长：960 宽、10–12 fps、≤ 90 秒通常可控制在 10MB 内。
- 技术复盘写法：结论先行 → 数据支撑 → 证据链接 → 反思（做错了什么 / 下一步）。
- 资料：https://getkap.co/ 、https://support.apple.com/guide/quicktime-player/record-your-screen-qtp97b08e666/mac 、https://ffmpeg.org/ffmpeg-filters.html#palettegen 、https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams

## 6. 执行步骤

### Step 1 · 90 秒 Demo 脚本（先写在 draft.md，照着录）

| 秒    | 镜头       | 操作                                              | 画面必须出现                                     |
| ----- | ---------- | ------------------------------------------------- | ------------------------------------------------ |
| 0–15  | ① 上传     | 打开 `/kb` → 拖入 `data/sample` 中一篇 md         | pending → processing → ready、分块数             |
| 15–40 | ② 库内提问 | `/` 问一个样例文档独有的问题                      | 「检索中」→ 逐字输出 → `[1]` chip → 右侧片段高亮 |
| 40–55 | ③ 库外提问 | 问「明天上海天气怎样」                            | 拒答样式 + 提示文案                              |
| 55–70 | ④ 反馈     | 对某条答案 👎 → 选「no_citation」→ 提交           | 「已反馈」                                       |
| 70–90 | ⑤ 评测     | 切到 VS Code 打开 `eval/reports/<报告>.md` 指标表 | hit@5 / 引用正确率 / 拒答率数字                  |

准备：浏览器开新的访客窗口（无书签栏、无扩展图标）、关闭通知（勿扰模式）、终端提示符不显示用户名路径、缩放 110% 让文字清晰。

### Step 2 · 录制 + 导出 GIF

- 方案 A（推荐）Kap：选区录制 1280×800 → 导出 GIF，FPS 12，宽度 960。
- 方案 B QuickTime（文件 → 新建屏幕录制）→ 得到 `demo.mov` → ffmpeg 转 GIF：

```bash
mkdir -p docs/assets
ffmpeg -i ~/Desktop/demo.mov \
  -vf "fps=10,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 docs/assets/demo.gif
ls -lh docs/assets/demo.gif        # > 10MB：fps 降到 8 或宽度降到 800 再转
```

原始 `.mov` 不入库（体积大），保存在本地 `~/lab/backups/media/`，W16 / W23 可复用。

### Step 3 · docs/portfolio/p1.md（8 问，每问 5–10 行）

先建骨架，再逐问填。**每个数字后面跟证据链接**（报告 / ADR / 代码路径），没有数据的写「未测」并说明原因。

```markdown
# P1 技术复盘：WorkPilot Knowledge（v0.5）

> 一句话：……；时间：W2–W8（约 \_\_ 小时）；仓库：<GitHub 链接>；Demo：docs/assets/demo.gif

## 1. 为什么需要 RAG？

- 问题：研发知识分散（规范 / 决策 / 组件用法），查找一次 10–30 分钟（DA-01 定义文档）
- 为什么不是微调 / 长上下文：知识频繁变化、需要可溯源引用、成本……
- 证据：docs/product/da01-definition.md

## 2. 为什么使用 Qdrant？ → 结论 + ADR 0002 + 实际用到的能力（payload 过滤 / hybrid / 快照恢复 RTO \_\_ 分钟）

## 3. Chunk 如何设计？ → 按标题结构切分 + 定长兜底；size/overlap 实验表（W5 Day20）：** vs ** 的 hit@5

## 4. Retrieval 如何评估？ → 50 题构成（库内 ** / 库外 ** / 多跳 \_\_）；hit@k、MRR、引用正确率、LLM-judge；基线 → 当前

## 5. 有哪些 Badcase？ → 分类统计表（检索未命中 ** / 引用错位 ** / 生成幻觉 ** / 语料缺失 **）；挑 2 条讲根因与修复

## 6. 如何降低幻觉？ → 引用约束 prompt（prompts/qa_answer.vN.md）、相似度阈值拒答、引用编号校验、拒答率 \_\_

## 7. 如何控制成本？ → 每次调用计量（W3 pricing）、单次问答 ¥\_\_、embedding 本地 / 同模型 API、上下文 top_k 控制、月成本估算

## 8. 如何部署？ → Compose + Caddy + 2C4G；request_id 日志、/ready、CI、备份 RTO \_\_ 分钟；ADR 0005

## 反思

- 做得好：……
- 做错 / 返工：……（例如：一开始没在 payload 存 doc_id，导致删除无法实现）
- 如果重做：……
- 下一步（P2）：把 kb_search 变成 Agent 工具（W9）

## 3 分钟讲稿

（见 Step 4）
```

写法：先让 Copilot 根据 `eval/reports/`、`badcases.md`、ADR 生成每问草稿，**你逐句核对数字**，删掉任何报告里找不到的数字。

### Step 4 · 3 分钟讲稿（约 750–850 字）

结构（每段约 30–40 秒）：

1. **问题**：我在研发工作中反复遇到 ……，每次 ……（15 秒）
2. **方案**：WorkPilot = 文档接入 + 带引用的 RAG + 拒答 + 反馈闭环；一句话架构（30 秒）
3. **关键设计**：手写 RAG 链路（为什么）、chunk 与 hybrid 实验、引用与拒答策略（45 秒）
4. **评测与结果**：50 题、指标从 ** 到 **、典型 badcase 与修复（45 秒）
5. **工程化**：流式 Web、Docker / Caddy 云部署、CI、备份恢复 RTO（30 秒）
6. **反思与下一步**：P2 Agent / MCP（15 秒）

用手机计时朗读一遍，超时就删形容词和过程描述，保留数字和取舍。

### Step 5 · 替换 README 占位 + 提交

README 中 `![demo](docs/assets/demo.gif)` 保留；在「评测结果」下加一行「完整复盘：docs/portfolio/p1.md」。

```bash
git add docs/assets/demo.gif docs/portfolio/p1.md README.md
git commit -m "docs: add 90s demo gif and P1 technical retrospective (8 questions)"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么 Demo 要包含「库外提问拒答」镜头？（答：证明系统不会编造，这是 RAG 可信度的核心卖点，也是面试官最关心的幻觉问题）
2. 「hit@5 = 0.86」该怎么向非技术面试官解释？（答：100 个问题里有 86 个，正确资料出现在系统找到的前 5 段中）
3. 为什么 8 问每个结论都要有证据链接？（答：面试会追问细节，链接让你能现场打开报告 / 代码；也防止自己记错或夸大）
4. 讲稿为什么要先讲问题再讲技术？（答：面试官评估的是「用技术解决问题」的能力，不是技术名词数量）

## 8. 对 DA-01 的贡献

P1 作品集的「Demo + Technical-Writeup」两项完成（总计划 §4.8 结构）。p1.md 也是 W16 技术文章、W23 Portfolio 网站 P1 页面、W25 面试题库的直接素材。

## 9. 求职映射（D 线）

- 岗位能力：项目叙事、量化表达、技术复盘
- 对应岗位：AI Engineer / GenAI Application Engineer / AI Full-Stack
- 简历 bullet 草稿：沉淀 RAG 项目技术复盘（8 个设计问题 + 50 题评测 + \_\_ 条 badcase 根因分析），配套 90 秒产品 Demo。
- 面试可能问：
  - 「你项目中最难的 badcase 是什么？怎么解决的？」要点：从 badcases.md 挑一条：现象 → 定位（检索 / 生成 / 语料）→ 修复 → 回归数字。
  - 「如何降低幻觉？」要点：检索质量（hybrid / rewrite）→ prompt 约束只基于上下文 → 阈值拒答 → 引用校验 → 评测拒答率；承认无法 100% 消除。

## 10. 卡住时的处理

| 现象                              | 处理                                                                             |
| --------------------------------- | -------------------------------------------------------------------------------- |
| GIF 超过 10MB                     | `fps=8`、`scale=800:-1`、`max_colors=64`；或把第 ⑤ 镜头改为静态截图单独放 README |
| 录制时 LLM 回答很慢 / 跑偏        | 提前问一次同样的问题确认答案质量；录制时可以剪掉等待段（Kap 支持裁剪首尾）       |
| 画面里出现了本机路径 / 用户名     | 重录或裁剪；终端用 `PS1='$ '` 临时简化提示符                                     |
| 8 问某项没有数据（例如 P95 未测） | 写「未测」+ 原因 + 计划在 Day33 补测；不编造                                     |
| 讲稿严重超时                      | 只保留每段 1 个数字 + 1 个取舍，删除「我们首先…然后…」类过程描述                 |

## 11. 产出记录（执行时填写）

- GIF 大小 / 时长：\_**\_ / \_\_**
- 录制次数：\_\_\_\_
- 讲稿实测时长：\_\_\_\_
- 发现但未修的 bug（记录到 Backlog）：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day32（GitHub 公开 + 简历条目 + 面试 10 题）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
