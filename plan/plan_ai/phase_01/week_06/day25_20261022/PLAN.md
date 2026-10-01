# Day 25 · 2026-10-22 · Week 06 Task 4：知识库管理页 + E2E 冒烟（v0.4）

## 0. 今天只做一件事

做出「浏览器上传文档 → 后台导入 → 状态变 ready → 可被问答引用 → 可删除 / 查看分块」的完整链路，打 tag `v0.4.0`，完成 Week 6 复盘。

不碰：多空间、权限、任务队列（Celery/Redis）、Gitea 仓库同步导入、重建索引按钮、PDF 版面解析优化。

## 1. 资产锚点

- 构建模块：M4.2 知识库管理、M2.6 KB API（upload / delete / chunks）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：**v0.4**（Web Console：流式 / 引用 / 历史 / 反馈 / 上传）
- 今天之后 WorkPilot 多了什么（可演示/可测量）：`/kb` 页拖拽上传 → pending → processing → ready（显示分块数）→ 提问可引用；删除后 Qdrant 点数为 0；Playwright E2E 一条
- 今日 AI 实际应用：把 W4 的 Ingest → Chunk → Embed → Upsert 管线包装成异步任务 + 状态机，这是所有企业 RAG 平台的「知识接入」标准形态

## 2. 起点（前置确认）

- 已有：W4 `app/rag/loaders`、`chunking`、`embedding`、`store`；Day24 的 `app/db`；MinIO / Qdrant 运行中。
- 需确认：

```bash
cd ~/lab/workpilot/apps/api
grep -rn "doc_id" app/rag/ | head                 # Qdrant payload 是否带 doc_id（删除 / 查分块要靠它过滤）
grep -rn "minio\|boto3" app/ | head               # W2/W4 用的哪种存储客户端
curl -s localhost:9000/minio/health/live -o /dev/null -w "%{http_code}\n"   # 200
curl -s localhost:6333/collections | python3 -m json.tool | head
```

若 payload 没有 `doc_id`：今天先在 upsert 处补上（老数据保持不变，新上传的才可删除）。

## 3. 验收对齐（做完要能勾掉）

- [ ] 上传 `sample.md` → 列表显示 pending/processing → 2 分钟内 ready 且 chunks > 0
- [ ] 聊天页问 sample.md 中的独有问题 → 答案引用该文档
- [ ] `.exe` → 415；11MB 文件 → 413；文件名 `../../evil.md` 存储时被清洗为 `evil.md`
- [ ] 导入失败（如上传损坏 PDF）→ 状态 failed 且显示错误原因
- [ ] 删除文档后：Qdrant 中该 `doc_id` 计数为 0，MinIO 对象不存在，列表消失
- [ ] E2E：Playwright 用例通过一次（或手工清单全部勾选，记录在 draft.md）
- [ ] `git tag v0.4.0` 已推送；周复盘已填写

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                                          |
| ------- | ------ | ------------------------------------------------------------- |
| 0–10    | P0     | 前置确认，`uv add python-multipart`                           |
| 10–45   | P0     | KBDocument 模型 + upload 路由（校验）+ `rag/jobs.py` 后台导入 |
| 45–60   | P0     | docs 列表 / 删除 / chunks 路由，curl 验证                     |
| 60–90   | P0     | KnowledgePage：上传、状态轮询、删除                           |
| 90–100  | P0     | tag `v0.4.0` + 周复盘                                         |
| 100–115 | P1     | Playwright E2E 一条；查看分块抽屉                             |
| 115–120 | P2     | 拖拽高亮样式、文件大小格式化                                  |

时间不足时最低保留：上传 + 状态 + 可问答 + tag；E2E 改为手工清单。

## 5. 今日学习（只学完成任务必须的）

- FastAPI `UploadFile` 依赖 `python-multipart`；文件名、扩展名、大小都是**不可信输入**，必须服务端校验。
- `BackgroundTasks` 在响应返回后于同进程执行（同步函数进线程池）；进程重启会丢任务——单机 Demo 够用，W19 再评估队列。
- Qdrant 按 payload 过滤删除：`FilterSelector(filter=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=...))]))`。
- 前端上传用 `FormData`，**不要手动设置 `Content-Type`**，让浏览器生成带 boundary 的头。
- 资料：https://fastapi.tiangolo.com/tutorial/request-files/ 、https://fastapi.tiangolo.com/tutorial/background-tasks/ 、https://qdrant.tech/documentation/concepts/points/#delete-points 、https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API 、https://playwright.dev/docs/intro

## 6. 执行步骤

### Step 1 · 文档表（追加到 app/db/models.py）

```python
class KBDocument(SQLModel, table=True):
    __tablename__ = "kb_document"
    id: str = Field(default_factory=new_id, primary_key=True)
    filename: str = Field(max_length=200)
    object_key: str | None = None                  # MinIO 中的 key
    size: int = 0
    status: str = Field(default="pending", index=True)   # pending / processing / ready / failed
    error: str | None = Field(default=None, max_length=500)
    chunks: int = 0
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
```

### Step 2 · 上传路由（app/routes/kb.py 中新增）——校验逻辑必须自己写

```python
import re
from pathlib import Path
from fastapi import BackgroundTasks, Depends, HTTPException, UploadFile

ALLOWED_EXT = {".md", ".pdf", ".html", ".txt"}
MAX_BYTES = 10 * 1024 * 1024


def clean_filename(name: str) -> str:
    name = Path(name or "").name                     # 去掉目录部分，防路径穿越
    name = re.sub(r"[^\w.\-]+", "_", name)[:120]     # \w 含中文；其余字符替换为 _
    return name.lstrip(".") or "file"


@router.post("/v1/kb/upload", status_code=202)
async def upload(file: UploadFile, bg: BackgroundTasks, s: Session = Depends(get_session)):
    filename = clean_filename(file.filename)
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(415, f"unsupported file type: {ext or 'none'}")
    data = await file.read(MAX_BYTES + 1)           # 最多读 10MB+1 字节，避免大文件撑爆内存
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "file too large (max 10MB)")
    if not data:
        raise HTTPException(400, "empty file")
    doc = KBDocument(filename=filename, size=len(data))
    doc.object_key = f"uploads/{doc.id}/{filename}"
    storage.put_bytes(doc.object_key, data)          # 复用 W2/W4 的 MinIO 客户端封装
    s.add(doc); s.commit()
    bg.add_task(ingest_document, doc.id)
    return {"id": doc.id, "status": doc.status}
```

MinIO 封装若没有，三行即可：`client.put_object(bucket, key, io.BytesIO(data), length=len(data))` / `client.get_object(bucket, key).read()` / `client.remove_object(bucket, key)`；启动时 `if not client.bucket_exists(bucket): client.make_bucket(bucket)`。

### Step 3 · 后台导入（app/rag/jobs.py）

```python
import logging, tempfile
from pathlib import Path
from sqlmodel import Session
from app.db.models import KBDocument, utcnow
from app.db.session import engine

logger = logging.getLogger(__name__)


def ingest_document(doc_id: str) -> None:
    with Session(engine) as s:
        doc = s.get(KBDocument, doc_id)
        if doc is None:
            return
        doc.status = "processing"; s.add(doc); s.commit()
        try:
            data = storage.get_bytes(doc.object_key)
            suffix = Path(doc.filename).suffix
            with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:   # W4 loader 读路径，这里落临时文件
                tmp.write(data); tmp.flush()
                docs = load_file(Path(tmp.name), doc_id=doc.id, title=doc.filename)
            chunks = chunk_documents(docs)                 # W4/W5 定下的切分配置
            doc.chunks = index_chunks(chunks)              # embed + upsert，payload 必含 doc_id
            doc.status, doc.error = "ready", None
        except Exception as e:                             # 后台任务无人接异常，必须自己落状态
            logger.exception("ingest failed doc_id=%s", doc_id)
            doc.status, doc.error = "failed", f"{type(e).__name__}: {e}"[:500]
        doc.updated_at = utcnow(); s.add(doc); s.commit()
```

`load_file / chunk_documents / index_chunks` 换成你 W4 的真实函数名；loader 若不接受 `doc_id/title`，在返回的 Document metadata 上覆盖。

### Step 4 · 列表 / 删除 / 分块

- `GET /v1/kb/docs`：`select(KBDocument).order_by(col(KBDocument.created_at).desc())`（替换 W4 的旧实现；CLI 导入的老文档不在表里——可接受，P2 写回填脚本）。
- `DELETE /v1/kb/docs/{id}`：Qdrant `client.delete(collection, points_selector=FilterSelector(filter=...doc_id...))` → MinIO `remove_object` → 删表记录；返回 204。
- `GET /v1/kb/docs/{id}/chunks`：`client.scroll(collection, scroll_filter=..., limit=200, with_payload=True, with_vectors=False)`，返回 `[{chunk_index, section, text}]`。

```bash
curl -s -F "file=@../../data/corpus/<任一公开文档>.md" localhost:8000/v1/kb/upload
curl -s localhost:8000/v1/kb/docs | python3 -m json.tool
curl -s -o /dev/null -w "%{http_code}\n" -F "file=@/bin/ls;filename=a.exe" localhost:8000/v1/kb/upload   # 415
```

### Step 5 · 知识库页（apps/web/src/pages/KnowledgePage.tsx）

`api/client.ts` 新增上传函数——**不能复用 `request()`**，因为它默认设了 JSON 的 Content-Type：

```ts
export async function uploadDoc(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/v1/kb/upload", { method: "POST", body: fd }); // 不设 Content-Type
  if (!res.ok)
    throw new ApiError(
      res.status,
      (await res.json().catch(() => ({})))?.detail ?? res.statusText,
    );
  return res.json() as Promise<{ id: string; status: string }>;
}
```

页面核心逻辑：

```tsx
const [docs, setDocs] = useState<KBDoc[]>([]);
const refresh = useCallback(async () => setDocs(await api.listDocs()), []);
useEffect(() => {
  refresh();
}, [refresh]);
useEffect(() => {
  // 有未完成的文档才轮询，2 秒一次
  if (!docs.some((d) => d.status === "pending" || d.status === "processing"))
    return;
  const t = setInterval(refresh, 2000);
  return () => clearInterval(t);
}, [docs, refresh]);

async function handleFiles(files: FileList | null) {
  for (const f of Array.from(files ?? [])) {
    try {
      await uploadDoc(f);
    } catch (e) {
      setError(`${f.name}：${(e as Error).message}`);
    }
  }
  refresh();
}
// 拖拽区：onDragOver={e => e.preventDefault()}  onDrop={e => { e.preventDefault(); handleFiles(e.dataTransfer.files) }}
// 另放 <input type="file" multiple accept=".md,.pdf,.html,.txt" onChange={e => handleFiles(e.target.files)} />
// 表格行 data-testid="doc-row"：文件名 / 大小 / 状态徽章（failed 时 title 显示 error）/ 分块数 / 「查看分块」/ 「删除」(confirm)
```

`App.tsx` 增加 `<Route path="/kb" element={<KnowledgePage />} />`。

### Step 6 · P1：Playwright E2E（apps/web/e2e/kb-flow.spec.ts）

```bash
cd ~/lab/workpilot/apps/web
pnpm add -D @playwright/test && pnpm exec playwright install chromium
mkdir -p e2e/fixtures   # 放一篇公开内容的 sample.md，含一个独有事实，如「WorkPilot 的吉祥物叫 Pilo」
```

`playwright.config.ts`：`testDir: 'e2e'`、`use: { baseURL: 'http://localhost:5173' }`、`timeout: 120_000`。

```ts
import { test, expect } from "@playwright/test";

test("upload → ready → ask with citation", async ({ page }) => {
  await page.goto("/kb");
  await page.setInputFiles("input[type=file]", "e2e/fixtures/sample.md");
  const row = page
    .getByTestId("doc-row")
    .filter({ hasText: "sample.md" })
    .first();
  await expect(row.getByText("ready")).toBeVisible({ timeout: 90_000 });

  await page.goto("/");
  await page.getByPlaceholder("输入问题").fill("WorkPilot 的吉祥物叫什么？");
  await page.getByRole("button", { name: "发送" }).click();
  await expect(page.getByTestId("citation-chip").first()).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByText("Pilo").first()).toBeVisible();
});
```

运行：先 `make dev` + `make web`，再 `pnpm exec playwright test`。该用例会真实调用 LLM（成本 < ¥0.01），**不进 CI**（Day29 CI 只跑不调外部 API 的测试）。时间不够则在 draft.md 写同样 5 步的手工清单并逐项勾选。

### Step 7 · 打 tag + 复盘 + 提交

```bash
cd ~/lab/workpilot
git add apps/api apps/web
git commit -m "feat(kb): upload with validation, background ingest, doc management page and e2e smoke"
git tag -a v0.4.0 -m "v0.4.0: web console (streaming, citations, history, feedback, kb management)"
git push && git push origin v0.4.0
```

填写 `plan/phase_01/week_06/README.md` 第 11 节周复盘；录 30 秒屏幕录制（上传 → 问答 → 引用）留作 W8 Demo 素材。

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么不能信任 `file.filename`？（答：客户端可控，可含 `../` 实现路径穿越或覆盖其他对象；必须取 basename 并白名单字符）
2. `await file.read(MAX_BYTES + 1)` 为什么要 +1？（答：读满 MAX+1 说明超限，可判 413，同时不会把超大文件全部读进内存）
3. 为什么上传接口返回 202 而不是 200？（答：请求已接受但处理在后台进行，状态需轮询查询）
4. 删除时为什么先删 Qdrant 再删表记录？（答：表记录是唯一索引来源；若先删记录、后删向量失败，就留下无法再定位的「孤儿向量」继续被检索到）
5. 进程重启时正在 processing 的文档会怎样？（答：BackgroundTasks 丢失，状态卡在 processing；可在启动时把 processing 改为 failed 并提示重传，W19 再评估队列）

## 8. 对 DA-01 的贡献

F1「数据接入 + 处理状态 + 失败原因 + 文档管理」落地，WorkPilot 从「开发者用脚本灌数据」变成「用户自己管理知识库」。v0.4 达成：Web Console 全部 P1 功能可演示，W7 的容器化与云部署直接以此为对象。

## 9. 求职映射（D 线）

- 岗位能力：文件上传安全、异步任务状态机、多存储一致性删除、E2E 测试
- 对应岗位：AI Full-Stack Engineer / AI Platform Engineer
- 简历 bullet 草稿：实现知识库文档管理（上传校验 / 异步解析入库 / 状态轮询 / 级联删除 Qdrant + MinIO），单文档 ≤10MB 平均 \_\_s 完成入库；以 Playwright 覆盖「上传 → 问答 → 引用」核心链路 E2E 冒烟。
- 面试可能问：
  - 「文件上传有哪些安全点？」要点：大小上限、扩展名 / 魔数校验、文件名清洗、存储隔离（对象存储而非 Web 目录）、解析器沙箱与超时。
  - 「导入是同步还是异步？为什么？」要点：异步 + 状态机；embedding 耗时不可控；失败可见可重试；单机用 BackgroundTasks，多实例用队列。

## 10. 卡住时的处理

| 现象                                                    | 处理                                                                                                      |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `Form data requires "python-multipart" to be installed` | `uv add python-multipart` 后重启                                                                          |
| 前端上传 422 `field required: file`                     | 手动设置了 `Content-Type: application/json` 或 multipart 无 boundary；用 FormData 且不设头                |
| 状态一直 pending                                        | 后台任务抛异常前就失败或 `--reload` 重启杀掉了任务：看 API 日志 `ingest failed`；手动改状态重传           |
| 删除后仍能检索到该文档                                  | 旧数据 payload 无 `doc_id` 或 key 名不一致：`client.count(collection, count_filter=..., exact=True)` 验证 |
| Playwright `Executable doesn't exist`                   | 未执行 `pnpm exec playwright install chromium`                                                            |
| `setInputFiles` 找不到元素                              | 页面有多个 file input 或被条件渲染：给 input 加 `data-testid` 并用 `getByTestId`                          |

## 11. 产出记录（执行时填写）

- sample.md 入库耗时 / 分块数：\_\_\_\_
- 415 / 413 / 文件名清洗验证：\_\_\_\_
- E2E 结果（Playwright / 手工）：\_\_\_\_
- v0.4.0 commit：\_\_\_\_
- 卡点：\_\_\_\_
- 用时：\_\_\_\_ 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 4 DONE → Week 6 DONE → 明天进入 Day26（Week 07 Task 1：Dockerfile + compose 全栈）。任一未通过 → 保持 IN PROGRESS，明天先补 P0（v0.4.0 tag 可推迟到补齐后再打）。
