# Day 15 · 2026-10-12 · Week 04 Task 1：语料准备 + Ingest

## 0. 今天只做一件事

按 da01-definition 的语料计划收集 ≥30 篇合规语料，并把 md / pdf / html 统一加载成 `Document` 对象（内容哈希去重），用 `ingest --dry-run` 输出统计。

不碰：分块、向量化、Qdrant（Day16）；上传接口（W6）；Gitea 仓库同步（W9 之后）。

## 1. 资产锚点

- 构建模块：M2.1 Ingest（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.2 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`data/corpus/` ≥30 篇语料 + `SOURCES.md`；`python -m app.rag.ingest --dry-run` 输出「文档数 / 总字符数 / 类型分布 / 去重数」
- 今日 AI 实际应用：RAG 的「感知/数据输入」环节 → 统一 `Document` + metadata 决定后续引用显示、过滤、按 workspace 隔离

## 2. 起点（前置确认）

- 已有：`docs/product/da01-definition.md`（语料计划 + 合规清单）、MinIO（9000，bucket `workpilot-raw`）、`.gitignore` 忽略 `data/*`。
- 需确认：

```bash
cd ~/lab/workpilot
grep -n "^data\|sample" .gitignore             # 期望：data/* 与 !data/sample/
docker ps --format '{{.Names}}\t{{.Status}}' | grep -i -E "minio|qdrant"
cd apps/api && uv run pytest -m "not llm" -q
```

## 3. 验收对齐（做完要能勾掉）

- [ ] `find ../../data/corpus -type f \( -name '*.md' -o -name '*.pdf' -o -name '*.html' \) | wc -l` ≥ 30
- [ ] 合规 grep 无命中；`data/corpus/SOURCES.md` 记录每类来源、仓库地址、commit、许可证
- [ ] `git status` 中看不到 `data/corpus`
- [ ] `uv run python -m app.rag.ingest --path ../../data/corpus --dry-run` 输出统计，且重复文件被计入「去重」
- [ ] `uv run pytest tests/test_loaders.py -q` 通过
- [ ] （P1）`--upload-raw` 后 MinIO Console 中可见 `default/<sha256>/<filename>` 对象
- [ ] 已 push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                  |
| ------- | ------ | ----------------------------------------------------- |
| 0–25    | P0     | 拉取公开文档子集 + 整理自有笔记 + 重写 3–5 篇规范样例 |
| 25–35   | P0     | 合规检查 + `SOURCES.md`                               |
| 35–55   | P0     | `models.py` + Markdown loader                         |
| 55–75   | P0     | PDF / HTML loader                                     |
| 75–90   | P0     | `ingest.py --dry-run` + 去重                          |
| 90–105  | P0     | loader 单测                                           |
| 105–120 | P1     | MinIO 原始文件上传 + 提交                             |

时间不足时最低保留：≥30 篇 md + Markdown loader + `--dry-run`（PDF/HTML/MinIO 顺延）。

## 5. 今日学习（只学完成任务必须的）

- `Document.id = sha256(text)`：同内容同 id，天然去重；但内容一改 id 就变，所以「更新」要按 `source` 路径替换（Day16 处理）。
- metadata 要在入口就定好：`path`（引用跳转）、`type`、`updated_at`、`workspace`（W19 多空间隔离的过滤字段）。
- PDF 文本抽取：`pypdf.PdfReader(path).pages[i].extract_text()`；扫描件抽不出文字，需跳过并告警（不做 OCR）。
- HTML 正文抽取：trafilatura 去导航/页脚，直接输出 Markdown，保留标题层级供 Day16 按标题切分。
- 资料：https://pypdf.readthedocs.io/en/stable/user/extract-text.html 、https://trafilatura.readthedocs.io/en/latest/usage-python.html 、https://docs.python.org/3/library/hashlib.html 、https://docs.pydantic.dev/latest/concepts/models/

## 6. 执行步骤

### Step 1 · 收集语料（按 da01-definition 第 4 节）

```bash
cd ~/lab/workpilot && mkdir -p data/corpus/{notes,oss,team,pdf,html} data/sample
TMP=$(mktemp -d)

# ② 公开文档：只拉需要的子目录（sparse checkout），记录 commit
git clone --depth 1 --filter=blob:none --sparse https://github.com/fastapi/fastapi.git $TMP/fastapi
git -C $TMP/fastapi sparse-checkout set docs/zh/docs/tutorial
git clone --depth 1 --filter=blob:none --sparse https://github.com/reactjs/zh-hans.react.dev.git $TMP/react
git -C $TMP/react sparse-checkout set src/content/learn
git clone --depth 1 --filter=blob:none --sparse https://github.com/vitejs/docs-cn.git $TMP/vite
git -C $TMP/vite sparse-checkout set guide

# 挑选与主场景相关的子集（每个项目 8–15 篇，不要整库）
mkdir -p data/corpus/oss/{fastapi,react,vite}
ls $TMP/fastapi/docs/zh/docs/tutorial | head -30      # 先看再挑
cp $TMP/fastapi/docs/zh/docs/tutorial/{first-steps,path-params,query-params,body}.md data/corpus/oss/fastapi/ 2>/dev/null
# react / vite 同理，按文件名挑选；挑完 ls 确认
for r in fastapi react vite; do echo "$r $(git -C $TMP/$r rev-parse --short HEAD)"; done   # 抄进 SOURCES.md
```

> 文件名以 `ls` 实际结果为准；若某仓库目录结构变化，在 GitHub 网页上确认路径后再 `sparse-checkout set`。

① 自有笔记：复制 `PROJECT_STANDARD.md`、`docs/adr/*.md`、`docs/product/da01-definition.md` 到 `data/corpus/notes/`。
③ 团队规范样例：在 `data/corpus/team/` 下**自己重写** 3–5 篇（如 `frontend-code-review.md`、`release-runbook.md`、`git-branching.md`），每篇 300–1500 字，带二三级标题。
④ PDF / HTML：把 1 篇规范样例用浏览器「打印 → 存储为 PDF」放到 `pdf/`；用 `curl -sL <公开文档页> -o data/corpus/html/<name>.html` 保存 2 个公开文档页（在 SOURCES.md 记录 URL）。

### Step 2 · 合规检查 + SOURCES.md

```bash
cd ~/lab/workpilot
# 把公司名、内部域名关键字替换成你自己的（不要写进任何提交文件）
grep -rInE "公司名关键字|内部域名关键字|password|secret|api[_-]?key|token=|10\.[0-9]+\.[0-9]+\.|192\.168\." data/corpus | head
git status --short | grep corpus && echo "!! corpus 未被忽略"
```

`data/corpus/SOURCES.md`：

```markdown
| 类别 | 路径         | 来源                                                   | commit / 日期 | 许可      | 合规检查            |
| ---- | ------------ | ------------------------------------------------------ | ------------- | --------- | ------------------- |
| oss  | oss/fastapi/ | github.com/fastapi/fastapi docs/zh/docs/tutorial       | abc1234       | MIT       | 公开文档            |
| oss  | oss/react/   | github.com/reactjs/zh-hans.react.dev src/content/learn | def5678       | CC BY 4.0 | 公开文档，保留署名  |
| team | team/\*.md   | 本人重写的通用规范样例                                 | 2026-10-12    | 自有      | 已 grep，无公司信息 |
```

复制一份到 `docs/product/corpus-sources.md`（可提交）；从 oss 中挑 ≤5 篇放 `data/sample/`（可提交，保留许可说明）。

### Step 3 · Document 模型 + Markdown loader（核心逻辑自己写）

```bash
cd apps/api && uv add pypdf trafilatura
mkdir -p app/rag/loaders && touch app/rag/__init__.py app/rag/loaders/__init__.py
```

`app/rag/models.py`：

```python
import hashlib
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel

class DocMeta(BaseModel):
    path: str
    type: Literal["md", "pdf", "html"]
    updated_at: str
    workspace: str = "default"

class Document(BaseModel):
    id: str                 # sha256(text)
    source: str             # 相对语料根目录的路径，如 oss/fastapi/query-params.md（引用与评测都用它）
    title: str
    text: str
    metadata: DocMeta

    @classmethod
    def create(cls, *, text: str, source: str, title: str, type: str, workspace: str, mtime: float) -> "Document":
        return cls(id=hashlib.sha256(text.encode("utf-8")).hexdigest(), source=source, title=title, text=text,
                   metadata=DocMeta(path=source, type=type, workspace=workspace,
                                    updated_at=datetime.fromtimestamp(mtime, timezone.utc).isoformat()))
```

`app/rag/loaders/markdown.py`：

```python
import re
from pathlib import Path
import yaml
from app.rag.models import Document

_FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

def load_markdown(path: Path, root: Path, workspace: str) -> Document:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    title = None
    if m := _FM.match(raw):                              # React/Vite 文档常带 front matter
        meta = yaml.safe_load(m.group(1)) or {}
        title = meta.get("title") if isinstance(meta, dict) else None
        raw = raw[m.end():]
    text = raw.strip()
    if not title:
        title = next((ln.lstrip("#").strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
    return Document.create(text=text, source=path.relative_to(root).as_posix(), title=title,
                           type="md", workspace=workspace, mtime=path.stat().st_mtime)
```

### Step 4 · PDF / HTML loader（样板可让 AI 生成，自己审）

- `loaders/pdf.py`：`PdfReader(path)`，各页 `extract_text() or ""` 用 `\n\n` 连接；title 取 `reader.metadata.title` 或文件名；**总文本 < 50 字符时返回 `None` 并打印「疑似扫描件，跳过」**。
- `loaders/html.py`：`trafilatura.extract(html, output_format="markdown", include_tables=True, include_links=False)`；返回 `None` 时回退 `BeautifulSoup(html, "html.parser")` 取 `<main>`/`<article>`/`<body>` + `markdownify`（需 `uv add beautifulsoup4 markdownify`，仅回退时需要）；title 取 `<title>`。
- `loaders/__init__.py`：

```python
from pathlib import Path
from app.rag.loaders.html import load_html
from app.rag.loaders.markdown import load_markdown
from app.rag.loaders.pdf import load_pdf

LOADERS = {".md": load_markdown, ".pdf": load_pdf, ".html": load_html, ".htm": load_html}

def load_dir(root: Path, workspace: str = "default") -> tuple[list, int]:
    docs, seen, dup = [], set(), 0
    for p in sorted(root.rglob("*")):
        fn = LOADERS.get(p.suffix.lower())
        if not fn or p.name == "SOURCES.md":
            continue
        doc = fn(p, root, workspace)
        if doc is None or not doc.text.strip():
            continue
        if doc.id in seen:
            dup += 1; continue
        seen.add(doc.id); docs.append(doc)
    return docs, dup
```

### Step 5 · ingest CLI（--dry-run）

`app/rag/ingest.py`：

```python
import argparse, asyncio
from collections import Counter
from pathlib import Path
from app.rag.loaders import load_dir

def parse_args():
    ap = argparse.ArgumentParser(description="WorkPilot ingest")
    ap.add_argument("--path", type=Path, required=True)
    ap.add_argument("--workspace", default="default")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--upload-raw", action="store_true", help="P1：原始文件上传 MinIO")
    return ap.parse_args()

async def main() -> None:
    a = parse_args()
    docs, dup = load_dir(a.path.resolve(), a.workspace)
    types = Counter(d.metadata.type for d in docs)
    chars = sum(len(d.text) for d in docs)
    print(f"docs={len(docs)} dup_skipped={dup} chars={chars} avg={chars // max(len(docs), 1)} types={dict(types)}")
    for d in sorted(docs, key=lambda d: len(d.text))[:3]:
        print(f"  最短: {d.source} ({len(d.text)} chars)")    # 检查是否有抽取失败的空壳文档
    if a.dry_run:
        return
    # Day16：chunk → embed → upsert

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
cd ~/lab/workpilot/apps/api
uv run python -m app.rag.ingest --path ../../data/corpus --dry-run
```

预期形如：`docs=38 dup_skipped=1 chars=152340 avg=4008 types={'md': 33, 'pdf': 2, 'html': 3}`。

### Step 6 · loader 单测

`tests/fixtures/`：放 1 个带 front matter 的 md、1 个小 PDF（用 data/sample 中导出的）、1 个 html。`tests/test_loaders.py` 断言：md 的 title 来自 front matter 且 text 不含 `---`；两个内容相同的 md 只产出 1 个 Document（dup=1）；pdf 文本非空；html 结果不含 `<nav`/`<script` 且含正文关键词。

### Step 7 · （P1）原始文件上传 MinIO

在 `ingest.py` 中 `--upload-raw` 时：`boto3.client("s3", endpoint_url=settings.minio_endpoint, aws_access_key_id=..., aws_secret_access_key=...)`，`upload_file(str(abs_path), "workpilot-raw", f"{workspace}/{doc.id}/{Path(doc.source).name}")`。凭据从 `.env` 读（`MINIO_ENDPOINT/MINIO_ACCESS_KEY/MINIO_SECRET_KEY`，在 `.env.example` 加键不加值）。在 http://localhost:9001 检查对象。

### Step 8 · 提交

```bash
cd ~/lab/workpilot
git status --short                       # 确认没有 data/corpus
git add apps/api docs/product/corpus-sources.md data/sample .env.example
git commit -m "feat(rag): document model and md/pdf/html loaders with dedup and dry-run ingest"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么用内容哈希做 `Document.id`？它带来什么问题？（答：天然去重、可复现；但内容变化 id 也变，需按 `source` 替换旧版本。）
2. `source` 存相对路径而不是绝对路径的原因？（答：换机器/容器路径不变，引用与评测的 `expected_sources` 可移植。）
3. 为什么 HTML 要转成 Markdown 而不是纯文本？（答：保留标题层级，Day16 按标题切分并记录 section。）
4. 扫描版 PDF 怎么处理？（答：文本过短判定为扫描件，跳过并告警；OCR 不在本阶段范围。）
5. 团队规范样例为什么必须「重写」？（答：合规红线：公司原文不能进入外部 LLM，也不能进入语料。）

## 8. 对 DA-01 的贡献

WorkPilot 有了第一批合规知识库语料和统一的数据入口（`Document` + metadata）。之后的分块、引用展示（`source`/`title`）、多空间隔离（`workspace`）和 W6 上传功能都建立在这个模型上。

## 9. 求职映射（D 线）

- 岗位能力：数据工程基础（多格式解析、清洗、去重、元数据设计）、数据合规意识。
- 对应岗位：AI Engineer、RAG Engineer、GenAI Application Engineer。
- 简历 bullet 草稿：「设计 RAG 数据接入层：统一 Document 模型（内容哈希去重 + 来源/类型/更新时间/空间元数据），支持 Markdown/PDF/HTML 解析，导入 ** 篇文档（** 万字），并建立语料来源与许可登记、敏感信息检查流程。」
- 面试可能问：
  1. 「PDF 解析有哪些坑？」——要点：扫描件无文本、多栏/表格顺序错乱、页眉页脚噪声；本项目检测扫描件跳过，复杂版式记 badcase。
  2. 「你的知识库怎么避免敏感数据？」——要点：语料分类与许可登记、只用公开/自有/重写样例、grep 检查、语料目录不入库、发布前检查。

## 10. 卡住时的处理

| 现象                                                 | 处理                                                                                            |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `git clone` 超时 / `Failed to connect to github.com` | 使用代理：`git -c http.proxy=http://127.0.0.1:7890 clone ...`；或直接在 GitHub 网页下载单个文件 |
| `sparse-checkout set` 后目录为空                     | 路径写错：去 GitHub 网页确认目录名（如 `docs/zh/docs/tutorial`），重新 set                      |
| `UnicodeDecodeError`                                 | 已用 `errors="ignore"`；若仍出错，文件可能不是 UTF-8，`file -I <path>` 查编码后转换             |
| `pypdf` 抽出文字全是乱码/空                          | 扫描件或字体编码问题，跳过该文件并记录到 SOURCES.md「已排除」                                   |
| `trafilatura.extract` 返回 `None`                    | 页面正文太短或结构特殊，走 bs4 + markdownify 回退                                               |
| `ModuleNotFoundError: No module named 'app'`         | 需在 `apps/api` 目录下运行 `uv run python -m app.rag.ingest`                                    |

## 11. 产出记录（执行时填写）

- 语料：notes ** / oss ** / team ** / pdf ** / html **，总计 ** 篇
- dry-run 输出：\_\_\_\_
- 合规 grep 结果：\_\_\_\_
- 排除的文件及原因：\_\_\_\_
- 卡点记录：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上（P1 项除外）→ Task 1 DONE → 明天进入 Day16（Chunking + Embedding + Qdrant 入库）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（语料 ≥30 篇与 Markdown loader 优先）。
