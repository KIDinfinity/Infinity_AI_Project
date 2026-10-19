# Day 15 · 2026-10-19 · 执行总结

> 对应 `PLAN.md`（Week 04 Task 1：语料准备 + Ingest）。
> 执行范围：Step 0–7 全部完成；Step 8（提交/推送）**按你的要求跳过，未提交代码**。

## 1. 一句话结论

在 `~/lab/workpilot` 完成第一批知识库语料（49 篇，含 md/pdf/html）与统一数据入口：
`Document` 模型 + Markdown/PDF/HTML loader + 内容哈希去重 + `ingest --dry-run`，并把原始文件上传 MinIO。
`--dry-run` 输出 `docs=49 dup_skipped=0 chars=399985 avg=8162 types={'html': 2, 'md': 46, 'pdf': 1}`。

## 2. 验收对齐（§3 逐项 + 可直接复制的完整命令）

> 所有命令从 `~/lab/workpilot` 出发。运行前确保 MinIO/Qdrant 容器已起（本机已起 12 天）。

### [x] 验收 1 — 语料 ≥ 30 篇

```bash
cd ~/lab/workpilot
find data/corpus -type f \( -name '*.md' -o -name '*.pdf' -o -name '*.html' \) | wc -l
```

预期输出：`49`（≥ 30 达标）。分类明细：

| 类别 | 篇数 |
| ---- | ---- |
| notes（自有笔记/项目文档） | 7 |
| oss/fastapi（公开文档） | 12 |
| oss/react（公开文档） | 12 |
| oss/vite（公开文档） | 10 |
| team（重写规范样例） | 5 |
| pdf（PDF 样本） | 1 |
| html（HTML 样本） | 2 |
| **合计** | **49** |

### [x] 验收 2 — 合规 grep 无命中 + SOURCES.md 记录

```bash
cd ~/lab/workpilot
grep -rInE "password|secret|api[_-]?key|token=|10\.[0-9]+\.[0-9]+\.|192\.168\." data/corpus
```

预期结果：**无真实密钥/内网 IP**。仅有的几处命中都是误报/公开文档正常内容：
- `oss/fastapi/response-model.md`：FastAPI 官方示例里的 `password` 字段说明（非密钥）
- `oss/react/keeping-components-pure.md`：React 文档标题「小秘密」里的「秘密」二字
- `html/*.html`：SVG path 坐标里的 `10.xxx` 数字片段（非 IP）

再跑一条（检查公司名/内部域名/内网 IP 关键词，可替换成你自己的关键字）：

```bash
cd ~/lab/workpilot
grep -rInE "公司名|内部域名|内网IP|订单号|用户信息" data/corpus
```

预期结果：`notes/pain-pool.md`、`notes/da01-definition.md` 中出现「公司/同事」均为**抽象化描述**（已去公司名/人名/产品名），非真实信息；无订单号、无用户信息。

来源登记文件（已就位）：

```bash
cd ~/lab/workpilot
ls -la data/corpus/SOURCES.md docs/product/corpus-sources.md
```

### [x] 验收 3 — git status 看不到 data/corpus

```bash
cd ~/lab/workpilot
git status --short
git check-ignore data/corpus
```

预期结果：
- `git status --short` 里**没有** `data/corpus`（只出现 `data/sample/*`、`docs/product/corpus-sources.md`、`apps/api/...`）
- `git check-ignore data/corpus` 输出 `data/corpus`（表示已被忽略）

### [x] 验收 4 — dry-run 输出统计 + 去重

```bash
cd ~/lab/workpilot/apps/api
uv run python -m app.rag.ingest --path ../../data/corpus --dry-run
```

预期输出（本机实测）：

```
docs=49 dup_skipped=0 chars=399985 avg=8162 types={'html': 2, 'md': 46, 'pdf': 1}
  最短: notes/adr-readme.md (69 chars)
  最短: notes/docs-readme.md (70 chars)
  最短: notes/adr-template.md (152 chars)
```

想现场看到「去重」被计入，可临时造一个重复文件再跑（跑完删除）：

```bash
cd ~/lab/workpilot
cp data/corpus/team/git-branching.md data/corpus/team/_dup_git-branching.md
cd apps/api && uv run python -m app.rag.ingest --path ../../data/corpus --dry-run
rm ~/lab/workpilot/data/corpus/team/_dup_git-branching.md
```

预期：第二次 dry-run 显示 `docs=50 dup_skipped=1`（重复文件被计入去重，不重复入库）。
去重的确定性验证由单测覆盖（见验收 5 的 `test_dedup_identical_content`）。

### [x] 验收 5 — loader 单测通过

```bash
cd ~/lab/workpilot/apps/api
uv run pytest tests/test_loaders.py -q
```

预期输出：`4 passed`。

```bash
cd ~/lab/workpilot/apps/api
uv run pytest -m "not llm" -q
```

预期输出：`36 passed, 2 deselected`（含既有 32 个 + 新增 4 个 loader 单测）。

### [x] 验收 6 — （P1）MinIO 上传后可见对象

上传原始文件：

```bash
cd ~/lab/workpilot/apps/api
uv run python -m app.rag.ingest --path ../../data/corpus --upload-raw
```

预期输出末尾：`uploaded=49 to MinIO bucket workpilot-raw`。

MinIO 存活检查（curl，无需签名）：

```bash
curl -s -o /dev/null -w 'minio live: %{http_code}\n' http://localhost:9000/minio/health/live
```

预期输出：`minio live: 200`。

列出桶内对象（S3 ListObjects 需 SigV4 签名，curl 手算签名不便，用这条完整 boto3 一行命令）：

```bash
cd ~/lab/workpilot/apps/api
uv run python -c "import boto3; from app.core.config import get_settings; s=get_settings(); s3=boto3.client('s3', endpoint_url=s.minio_endpoint, aws_access_key_id=s.minio_access_key, aws_secret_access_key=s.minio_secret_key.get_secret_value(), region_name='us-east-1'); objs=s3.list_objects_v2(Bucket='workpilot-raw').get('Contents',[]); print('objects =', len(objs)); [print(' ', o['Key']) for o in objs[:5]]"
```

预期输出形如：

```
objects = 50
  default/009a1658.../using-plugins.md
  default/022e2b5a.../body.md
  default/05aa802b.../docs-readme.md
```

（key 结构为 `default/<sha256>/<filename>`，符合 PLAN 预期；桶内多出的 1 个是历史遗留对象。）

可视化查看：浏览器打开 `http://localhost:9001` → 用 `.env` 里的 MinIO 凭据登录 → `Buckets → workpilot-raw` → 展开 `default/<sha256>/`。

### [ ] 验收 7 — 已 push

**跳过。** 按你的要求「不用帮我提交代码」，Step 8 的 `git add / commit / push` 未执行。
当前改动留在工作区，可用下面命令查看（只读，不提交）：

```bash
cd ~/lab/workpilot
git status --short
```

## 3. 各 Step 做了什么

- **Step 0 起点确认**：`.gitignore` 已忽略 `data/*` 且放行 `!data/sample/`；MinIO/Qdrant 容器 Up 12 天；基线测试 `32 passed, 2 deselected`。
- **Step 1 收集语料**：建 `data/corpus/{notes,oss,team,pdf,html}`；SSH sparse-checkout 拉取 fastapi/react/vite 三个仓库的文档子集（commit：fastapi `e5fc7ef`、react `cbd15b3`、vite `dc1f526`）；复制 7 篇自有笔记；重写 5 篇团队规范样例；生成 1 个 PDF + 保存 2 个公开网页 HTML。合计 49 篇。
- **Step 2 合规 + SOURCES.md**：grep 无真实敏感信息命中；`data/corpus/SOURCES.md` 与可提交副本 `docs/product/corpus-sources.md` 已写；从 oss 挑 5 篇进 `data/sample/` 并更新其 README（保留署名与许可）。
- **Step 3 Document 模型 + Markdown loader**：`app/rag/models.py`（`Document.id = sha256(text)` + `DocMeta`）、`app/rag/loaders/markdown.py`（front matter 取 title）。
- **Step 4 PDF/HTML loader**：`loaders/pdf.py`（pypdf，<50 字符判扫描件跳过）、`loaders/html.py`（trafilatura → bs4+markdownify 回退）、`loaders/__init__.py`（`LOADERS` 注册表 + `load_dir` 去重）。
- **Step 5 ingest CLI**：`app/rag/ingest.py`（`--path/--workspace/--dry-run/--upload-raw`），输出文档数/字符数/类型分布/最短文档。
- **Step 6 loader 单测**：`tests/test_loaders.py`（4 个用例：front matter 标题、内容哈希去重、PDF 非空、HTML 去 nav/script）+ `tests/fixtures/`（md/pdf/html 各一）。
- **Step 7 MinIO 上传**：`--upload-raw` 上传 49 个原始文件到 `workpilot-raw`，key 为 `default/<sha256>/<filename>`。
- **Step 8 提交**：跳过（未提交）。

## 4. 产出记录（§11 填写）

- 语料：notes 7 / oss 34（fastapi 12 + react 12 + vite 10）/ team 5 / pdf 1 / html 2，总计 **49** 篇
- dry-run 输出：`docs=49 dup_skipped=0 chars=399985 avg=8162 types={'html': 2, 'md': 46, 'pdf': 1}`
- 合规 grep 结果：无真实密钥/内网 IP；命中均为公开文档示例与 SVG 坐标误报；无真实业务数据
- 排除的文件及原因：无
- 卡点记录：
  1. `cupsfilter` 无法把 `text/html` 转 PDF（报「无滤镜」），改用 `reportlab`（UnicodeCIDFont STSong-Light）生成可抽取文本的 PDF。
  2. 本机 7890 代理未运行、GitHub HTTPS 被阻断，`git clone` 改用 SSH（`git@github.com:...`）。
- 用时：约 40 分钟（含克隆/装依赖）

## 5. 概念自检（§7 答案，简短）

1. 内容哈希做 `Document.id`：天然去重、可复现；但内容一改 id 就变，更新要按 `source` 替换旧版本（Day16 处理）。
2. `source` 存相对路径：换机器/容器路径不变，引用与评测的 `expected_sources` 可移植。
3. HTML 转 Markdown 而非纯文本：保留标题层级，Day16 按标题切分并记录 section。
4. 扫描版 PDF：文本过短判定为扫描件，跳过并告警；OCR 不在本阶段范围。
5. 团队规范样例必须「重写」：合规红线，公司原文不能进外部 LLM，也不能进语料。

## 6. 新增/修改文件清单（未提交）

新增：
- `apps/api/app/rag/__init__.py`、`models.py`、`ingest.py`
- `apps/api/app/rag/loaders/__init__.py`、`markdown.py`、`pdf.py`、`html.py`
- `apps/api/tests/test_loaders.py`、`apps/api/tests/fixtures/{md_frontmatter.md, sample.html, sample.pdf}`
- `docs/product/corpus-sources.md`
- `data/sample/{fastapi-first-steps.md, react-your-first-component.md, react-responding-to-events.md, vite-why.md, vite-using-plugins.md}`

修改：
- `apps/api/app/core/config.py`（新增 `minio_endpoint/minio_access_key/minio_secret_key` 字段）
- `apps/api/pyproject.toml`、`apps/api/uv.lock`（新增 `pypdf/trafilatura/beautifulsoup4/markdownify/boto3`）
- `data/sample/README.md`（补充样例来源与许可表）

被 `.gitignore` 忽略、未进入 git：
- `data/corpus/`（49 篇语料 + `SOURCES.md`）

## 7. 下一步

P0 全部完成 → Task 1 DONE → 明天进入 **Day16（Chunking + Embedding + Qdrant 入库）**。
