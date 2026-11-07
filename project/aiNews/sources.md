# sources.md —— 信息源清单（唯一事实来源）

> `COLLECT_PROMPT.md` 每次执行时必须先读本文件，拿到「可用」状态的源去收集；执行过程中如果发现某个源打不开/被墙/工具调不通，**直接回来改本文件**（标记状态 + 写自愈变更日志），不要把问题记在别的地方。

## 1. 信息源清单

| 名称                 | 类型        | 链接                                   | 状态 | 最近确认日期 | 备注                              |
| -------------------- | ----------- | -------------------------------------- | ---- | ------------ | --------------------------------- |
| Hacker News          | 综合技术/AI | https://news.ycombinator.com/          | 可用 | 2026-11-07   | 看首页 + 搜索 "AI"/"LLM" 相关热帖 |
| Hugging Face Papers  | 论文/模型   | https://huggingface.co/papers          | 可用 | 2026-11-07   | 每日热门论文                      |
| OpenAI News          | 官方动态    | https://openai.com/news/               | 可用 | 2026-11-07   | 模型/产品发布                     |
| Anthropic News       | 官方动态    | https://www.anthropic.com/news         | 可用 | 2026-11-07   | 模型/产品发布                     |
| Google DeepMind Blog | 官方动态    | https://deepmind.google/discover/blog/ | 可用 | 2026-11-07   | 模型/研究发布                     |
| 机器之心             | 中文媒体    | https://www.jiqizhixin.com/            | 可用 | 2026-11-07   | 中文 AI 行业动态                  |
| 量子位               | 中文媒体    | https://www.qbitai.com/                | 可用 | 2026-11-07   | 中文 AI 行业动态                  |
| GitHub Trending      | 开源趋势    | https://github.com/trending            | 可用 | 2026-11-07   | 看 AI/LLM 相关仓库榜单            |

> 状态只有三种：`可用` / `待验证`（新加但没实际跑过）/ `失效-日期`（跑的时候发现打不开或工具用不了）。

## 2. 替补源（当主力源失效时优先尝试，按需补充）

| 名称                 | 链接                                 | 说明                                 |
| -------------------- | ------------------------------------ | ------------------------------------ |
| 36氪 AI 频道         | https://36kr.com/information/AI/     | 中文行业动态替补                     |
| Reddit r/LocalLLaMA  | https://www.reddit.com/r/LocalLLaMA/ | 开源模型/本地部署动态替补            |
| arXiv cs.AI 最新列表 | https://arxiv.org/list/cs.AI/recent  | 论文替补（信息密度高，筛选成本也高） |

## 3. 自愈变更日志

> 每次执行中遇到「网站打不开 / 工具调不通」导致需要调整本文件，都在下面追加一条，格式：`- YYYY-MM-DD｜源名｜问题｜处理方式`。不要删除历史记录。

（暂无记录）
