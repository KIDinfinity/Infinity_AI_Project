# Day 23 · 2026-11-03 · Week 06 Task 2：流式渲染 + 引用面板 + 状态

## 0. 今天只做一件事

用 fetch + ReadableStream 手动解析 `/v1/kb/ask/stream` 的 SSE，让答案逐字出现、`[n]` 变成可点击引用 chip、右侧面板显示原文片段，并有 idle / retrieving / streaming / done / error 五种状态。

不碰：数据库与历史（Day24）、上传（Day25）、引用片段关键词高亮、动画。

## 1. 资产锚点

- 构建模块：M4.1 Chat（流式 + 引用面板）（见 plan/plan_ai/DA01_TARGET_ASSET.md §5）
- 版本里程碑：为 v0.4 做准备
- 今天之后 WorkPilot 多了什么（可演示/可测量）：首 token 前显示「检索中」→ 逐字输出 → 点 `[2]` 右侧高亮第 2 条引用（标题 / 章节 / 片段 / 分数）；库外问题显示拒答样式；可随时停止
- 今日 AI 实际应用：W3 的 SSE 流式 + W4 的 Grounded Answer（引用编号、拒答）第一次以「用户可感知」的形式呈现；Markdown 安全渲染是 LLM 输出处理（OWASP LLM02 不安全输出处理）的前端实践

## 2. 起点（前置确认）

- 已有：Day22 的 `apps/web`、`api/client.ts`、`ChatPage`；后端 `/v1/kb/ask/stream` 输出 `retrieved → token → done`。
- 需确认真实帧格式（**下面代码里的字段名以此为准**）：

```bash
curl -N -X POST localhost:8000/v1/kb/ask/stream \
  -H 'Content-Type: application/json' -d '{"question":"Qdrant 的 payload 过滤怎么用？"}'
# 期望：event: retrieved / data: {"citations":[{"index":1,"doc_id":..,"title":..,"section":..,"text":..,"score":0.71}]}
#       event: token / data: {"text":"Qdrant"} …… event: done / data: {"refused":false,"usage":{...}}
```

若 `done` 里没有 `refused`，今天 P0 顺手在后端补上（拒答判断 W4 已有，只是透传）。

## 3. 验收对齐（做完要能勾掉）

- [ ] 提问后先显示「正在检索知识库…」，随后答案逐字出现
- [ ] 答案中的 `[n]` 显示为 chip，点击后右侧第 n 条引用高亮并滚动到可见
- [ ] 引用卡片显示：文档标题、章节、片段（截断）、分数（2 位小数）
- [ ] 流式中点「停止」→ Network 面板显示请求 canceled，状态回到 idle
- [ ] 库外问题（如「今天上海天气」）显示拒答样式；停掉 API 后提问显示错误条 + 重试
- [ ] 答案文本里含 `<img src=x onerror=alert(1)>` 时不弹窗（见 Step 6 自测）
- [ ] 已 commit + push

## 4. 时间块（≤ 120 分钟）

| 时间    | 优先级 | 内容                                            |
| ------- | ------ | ----------------------------------------------- |
| 0–10    | P0     | `curl -N` 记录真实帧格式                        |
| 10–40   | P0     | `lib/sse.ts` + `hooks/useStreamingAnswer.ts`    |
| 40–60   | P0     | `AnswerMarkdown`（markdown 三件套 + 引用 chip） |
| 60–85   | P0     | `CitationPanel` + ChatPage 两栏布局接入         |
| 85–100  | P0     | 状态 / 拒答 / 错误 / 停止；XSS 自测；提交       |
| 100–115 | P1     | `@tailwindcss/typography` 让 Markdown 排版好看  |
| 115–120 | P2     | 引用卡片显示「在答案中被引用 x 次」             |

时间不足时最低保留：流式逐字 + 引用 chip 点击 → 右侧显示片段。

## 5. 今日学习（只学完成任务必须的）

- SSE 帧以空行（`\n\n`）分隔，帧内每行 `field: value`；`data:` 可多行拼接；以 `:` 开头的是注释 / 心跳。
- `TextDecoderStream` 会正确处理被网络拆开的多字节 UTF-8 中文字符（手写 `TextDecoder.decode(chunk)` 不带 `{stream:true}` 会乱码）。
- react-markdown 默认不渲染原始 HTML；再加 rehype-sanitize 做白名单清洗，是纵深防御。`EventSource` 只支持 GET，所以 POST 流式必须 fetch + `response.body` 自己解析。
- 资料：https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events 、https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream 、https://developer.mozilla.org/en-US/docs/Web/API/AbortController 、https://github.com/remarkjs/react-markdown 、https://github.com/rehypejs/rehype-sanitize

## 6. 执行步骤

### Step 1 · SSE 帧解析（src/lib/sse.ts）——必须自己逐行理解

先在 `src/types/ui.ts` 写：`Citation = { index; doc_id; title; section?; text; score }`、`StreamStatus = "idle" | "retrieving" | "streaming" | "done" | "error"`。

```ts
export type SSEMessage = { event: string; data: string };

export async function* readSSE(
  body: ReadableStream<Uint8Array>,
): AsyncGenerator<SSEMessage> {
  const reader = body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value.replace(/\r\n/g, "\n");
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, sep); // 一个完整帧
      buffer = buffer.slice(sep + 2); // 剩余部分留到下一轮（可能是半帧）
      const msg = parseFrame(frame);
      if (msg) yield msg;
    }
  }
}

function parseFrame(frame: string): SSEMessage | null {
  let event = "message";
  const data: string[] = [];
  for (const line of frame.split("\n")) {
    if (!line || line.startsWith(":")) continue; // 空行 / 心跳注释
    const i = line.indexOf(":");
    const field = i === -1 ? line : line.slice(0, i);
    let value = i === -1 ? "" : line.slice(i + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    else if (field === "data") data.push(value);
  }
  return data.length ? { event, data: data.join("\n") } : null;
}
```

### Step 2 · 流式 Hook（src/hooks/useStreamingAnswer.ts）

```ts
import { useCallback, useRef, useState } from "react";
import { readSSE } from "../lib/sse";
import type { Citation, StreamStatus } from "../types/ui";

type State = {
  status: StreamStatus;
  answer: string;
  citations: Citation[];
  error: string | null;
};
const INIT: State = { status: "idle", answer: "", citations: [], error: null };

export function useStreamingAnswer() {
  const [state, setState] = useState<State>(INIT);
  const ctrlRef = useRef<AbortController | null>(null);

  const start = useCallback(async (question: string, extra = {}) => {
    ctrlRef.current?.abort(); // 新问题取消旧请求
    const ctrl = (ctrlRef.current = new AbortController());
    setState({ ...INIT, status: "retrieving" });
    let answer = "";
    let citations: Citation[] = [];
    try {
      const res = await fetch("/v1/kb/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, ...extra }),
        signal: ctrl.signal,
      });
      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);
      for await (const { event, data } of readSSE(res.body)) {
        const p = JSON.parse(data);
        if (event === "retrieved") citations = p.citations ?? [];
        if (event === "token") answer += p.text ?? "";
        if (event === "error") throw new Error(p.message ?? "服务端错误");
        const status: StreamStatus =
          event === "done" ? "done" : answer ? "streaming" : "retrieving";
        setState({ status, answer, citations, error: null });
        if (event === "done")
          return { answer, citations, refused: !!p.refused, done: p };
      }
      throw new Error("流意外结束（未收到 done）");
    } catch (e) {
      const aborted = ctrl.signal.aborted; // 用户点停止不算错误
      const error = aborted ? null : String(e);
      setState((s) => ({ ...s, status: aborted ? "idle" : "error", error }));
      return null;
    }
  }, []);

  const stop = useCallback(() => ctrlRef.current?.abort(), []);
  return { ...state, start, stop };
}
```

### Step 3 · 安全 Markdown + 引用 chip（src/components/AnswerMarkdown.tsx）

```bash
cd ~/lab/workpilot/apps/web && pnpm add react-markdown remark-gfm rehype-sanitize
```

```tsx
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

// 把 [3] 改写成指向 #cite-3 的链接，再在 a 组件里渲染成 chip
const toCiteLinks = (s: string) =>
  s.replace(/\[(\d{1,2})\](?!\()/g, "[$1](#cite-$1)");

export function AnswerMarkdown({
  text,
  onCite,
}: {
  text: string;
  onCite: (n: number) => void;
}) {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]} // 白名单清洗：去掉 script / on* 属性 / javascript: 链接
        components={{
          a: ({ href, children }) => {
            const m = href?.match(/^#cite-(\d+)$/);
            if (m)
              return (
                <button
                  type="button"
                  data-testid="citation-chip"
                  onClick={() => onCite(Number(m[1]))}
                  className="mx-0.5 rounded bg-blue-100 px-1.5 align-super text-xs text-blue-700 hover:bg-blue-200"
                >
                  {m[1]}
                </button>
              );
            return (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            );
          },
        }}
      >
        {toCiteLinks(text)}
      </ReactMarkdown>
    </div>
  );
}
```

### Step 4 · 引用面板 + 接入 ChatPage

`src/components/CitationPanel.tsx`（让 Copilot 生成样式，你只写逻辑）：props `citations: Citation[]`、`active: number | null`；每张卡片 `id={'cite-card-' + c.index}`，`active === c.index` 时加 `ring-2 ring-blue-500`；`useEffect` 中 `document.getElementById('cite-card-' + active)?.scrollIntoView({ block: 'nearest' })`；片段 `line-clamp-6`，分数 `c.score.toFixed(2)`。

ChatPage 改造要点：

- `const { status, answer, citations, error, start, stop } = useStreamingAnswer()`；`ChatMessage` 增加 `citations?`、`refused?`；`const r = await start(question)`，`r` 非空时 push 助手消息（content / citations / refused）。
- 已完成消息用 `<AnswerMarkdown>`；`retrieving` 时显示「正在检索知识库…」，`streaming` 时渲染 `<AnswerMarkdown text={answer}/>` + 闪烁光标。
- `refused` → 琥珀色边框 +「知识库中没有找到可靠依据」；`error` → 红色条 + 重试按钮（重新 `start` 上一个问题）。
- 发送按钮在 retrieving / streaming 时变为「停止」（`onClick={stop}`）；布局 `grid grid-cols-[1fr_320px]`，右栏 `<CitationPanel>` 显示当前选中消息的引用。

### Step 5 · 安全自测 + P1 排版 + 提交

XSS 自测：临时在 ChatPage 渲染 `<AnswerMarkdown text={'测试 <img src=x onerror=alert(1)> [链接](javascript:alert(1)) [1]'} onCite={setActive} />`，确认：无弹窗、HTML 被显示为文本或被移除、`javascript:` 链接不可执行、`[1]` 是 chip。确认后删除临时代码。

P1：`pnpm add -D @tailwindcss/typography`，在 `index.css` 第二行加 `@plugin "@tailwindcss/typography";`，`prose` 类生效。

```bash
pnpm exec tsc --noEmit -p tsconfig.app.json
cd ~/lab/workpilot && git add apps/web
git commit -m "feat(web): streaming answer via fetch SSE parser, citation chips and panel"
git push
```

## 7. 概念自检（不看资料，口述，附答案）

1. 为什么不用 `EventSource`？（答：只支持 GET、不能带 JSON body 和自定义 header；问答需要 POST）
2. 为什么 buffer 处理完帧后要保留剩余部分？（答：网络 chunk 边界与 SSE 帧边界无关，一个 chunk 可能包含半帧，必须拼到下一轮）
3. 中文为什么可能乱码，`TextDecoderStream` 怎么解决？（答：一个汉字 3 字节可能被拆到两个 chunk；流式解码器会缓存不完整字节直到凑齐）
4. AbortController 取消后，后端还会继续消耗 token 吗？（答：取决于后端是否检测断连；FastAPI StreamingResponse 在客户端断开后写入失败会停止生成器，但已发出的 LLM 请求可能已计费——可在后端用 `request.is_disconnected()` 及早退出）
5. 为什么既用 react-markdown 默认不渲染 HTML，又加 rehype-sanitize？（答：纵深防御；将来若有人加 rehype-raw 或自定义插件，sanitize 仍兜底；还会清洗 `javascript:` 等危险 URL）

## 8. 对 DA-01 的贡献

F2「流式回答 + 段落级引用 + 明确拒答」在产品层面第一次完整可见。`useStreamingAnswer` 与 `readSSE` 会在 W10 Agent 步骤时间线（SSE 步骤事件）中直接复用。

## 9. 求职映射（D 线）

- 岗位能力：AI UX（流式、引用溯源、拒答态）、浏览器流 API、前端安全
- 对应岗位：AI Full-Stack / GenAI Application Engineer / 前端（AI 方向）
- 简历 bullet 草稿：实现基于 fetch + ReadableStream 的 SSE 解析器与可取消流式渲染，首字延迟由非流式 {x}s 降至 {x}s；答案引用以 chip 形式可点击溯源到原文片段（标题 / 章节 / 相似度）；LLM 输出经 rehype-sanitize 白名单清洗防 XSS。
- 面试可能问：
  - 「流式输出前端怎么做？」要点：POST + ReadableStream；按 `\n\n` 分帧；事件类型驱动状态机；Abort 取消；中文拆包。
  - 「怎么让用户信任 RAG 答案？」要点：引用可点击回原文、展示相似度、无依据明确拒答、反馈入口（Day24）。

## 10. 卡住时的处理

| 现象                                                  | 处理                                                                                                                |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 答案一次性出现而非逐字                                | 后端或代理在缓冲：确认后端返回 `media_type="text/event-stream"`；`curl -N` 直连 8000 若也是一次性，问题在后端生成器 |
| `SyntaxError: Unexpected token ... is not valid JSON` | token 帧的 data 不是 JSON（是纯文本）：改为 `event === 'token' ? data : JSON.parse(data)` 分支处理                  |
| 点击 chip 页面跳到顶部 / URL 出现 `#cite-1`           | 说明 chip 被渲染成了 `<a>`：检查 `components.a` 的正则与 `toCiteLinks` 输出是否一致                                 |
| 停止后仍显示错误条                                    | catch 中必须先判断 `ctrl.signal.aborted`（用户主动取消不算错误）；`prose` 类无效则是未装 typography（P1）           |

## 11. 产出记录（执行时填写）

- 真实事件名 / 字段：{待填}；首 token 延迟：{待填} s；XSS 自测结果：{待填}
- 卡点：{待填}；用时：{待填} 分钟

## 12. 完成判定

第 3 节全部勾上 → Task 2 DONE → 明天进入 Day24（会话历史 SQLite + 反馈）。任一未通过 → 保持 IN PROGRESS，明天先补 P0。
