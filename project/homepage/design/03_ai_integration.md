# 03 — AI 集成方案

## 1. 模型选择与配置

### 1.1 首选：Google Gemini Flash 2.0

```
Model:        gemini-2.0-flash-001
Provider:     Google AI (generativelanguage.googleapis.com)
免费额度:     15 RPM / 1500 RPD（requests per day）
Context:      1M tokens（但我们限制到 2048）
调用方式:     @google/generative-ai SDK 或 REST API
```

### 1.2 备选：DeepSeek V3

```
Model:        deepseek-chat
Provider:     DeepSeek (api.deepseek.com)
免费额度:     500 次/天（新用户注册赠送 10M tokens）
Context:      64K tokens
调用方式:     OpenAI 兼容 API（用 openai npm 包改 baseURL）
```

### 1.3 本地开发：Ollama

```
Model:        qwen2.5:3b 或 llama3.2:3b
Provider:     本地 Ollama
免费额度:     无限（本地 GPU/CPU）
调用方式:     ollama npm 包 或 OpenAI 兼容 API (http://localhost:11434/v1)
```

## 2. Token 限制实现

### 2.1 限制策略

```typescript
// src/lib/constants.ts
export const AI_CONFIG = {
  MAX_INPUT_TOKENS: 1500, // 用户输入上限
  MAX_OUTPUT_TOKENS: 1024, // AI 输出上限
  MAX_TOTAL_TOKENS: 2048, // 单次请求总上限
  TRUNCATE_WARNING: 1200, // 超过此值显示警告
} as const;
```

### 2.2 Token 计数

使用 `gpt-tokenizer` 包（轻量，支持 cl100k_base 编码，与大多数模型兼容）：

```typescript
// src/lib/tokenizer.ts
import { encode, decode } from "gpt-tokenizer";

export function countTokens(text: string): number {
  return encode(text).length;
}

export function truncateByTokens(text: string, maxTokens: number): string {
  const tokens = encode(text);
  if (tokens.length <= maxTokens) return text;
  return decode(tokens.slice(0, maxTokens));
}
```

### 2.3 前端硬限制流程

```typescript
// 在 useAiChat hook 中
async function sendMessage(userInput: string) {
  const inputTokens = countTokens(userInput + systemPrompt);

  if (inputTokens > AI_CONFIG.MAX_INPUT_TOKENS) {
    // 截断用户输入
    const availableForUser = AI_CONFIG.MAX_INPUT_TOKENS - countTokens(systemPrompt);
    userInput = truncateByTokens(userInput, availableForUser);
    showWarning('输入过长，已自动截断');
  }

  // 调用 AI，max_tokens 硬编码为 MAX_OUTPUT_TOKENS
  const response = await aiClient.chat({
    messages: [...],
    maxTokens: AI_CONFIG.MAX_OUTPUT_TOKENS,
    stream: true,
  });
}
```

## 3. Prompt 设计

### 3.1 Demo 1：智能问答

```typescript
const CHAT_SYSTEM_PROMPT = `你是一个个人技术主页的 AI 助手。你的知识范围仅限于以下内容：

## 关于站长
- 全栈工程师，5 年经验，主攻前端（React/TypeScript）
- AI 应用方向：LLM、RAG、Agent、MCP
- 当前在做 WorkPilot：一个可私有部署的研发工作 AI 助手平台

## 技术栈
前端：React, TypeScript, Next.js, Tailwind CSS, Vite
后端：Python, FastAPI, PostgreSQL
AI：LangChain, LlamaIndex, OpenAI API, Gemini API, Ollama
DevOps：Docker, GitHub Actions, Vercel

## 规则
- 只回答上述范围内的内容
- 如果被问到范围外的问题，礼貌说明你只能回答关于站长技术栈的问题
- 回答简洁，不超过 200 字
- 使用中文`;
```

### 3.2 Demo 2：代码解释/转换

```typescript
const CODE_SYSTEM_PROMPT = `你是一个代码助手。根据用户选择的模式返回结果。

## 输出格式（必须是合法 JSON）
{
  "explanation": "对代码的简要解释（中文，不超过 150 字）",
  "code": "转换后的代码（仅当模式为语言转换时返回，否则为 null）"
}

## 模式
- explain: 只解释代码，不转换
- python / typescript / go: 将代码转换为目标语言

## 规则
- 只返回 JSON，不要任何额外文字
- 如果代码不完整或无法理解，explanation 中说明
- 转换时保持原逻辑，不添加新功能`;
```

### 3.3 Demo 3：文档摘要

```typescript
const SUMMARY_SYSTEM_PROMPT = `你是一个文档摘要助手。对用户提供的文本生成简洁摘要。

## 输出格式（必须是合法 JSON）
{
  "summary": "3 句话以内的中文摘要",
  "keywords": ["关键词1", "关键词2", "关键词3"]
}

## 规则
- 只返回 JSON，不要任何额外文字
- 摘要控制在 3 句话以内
- 关键词 3-5 个，按重要性排序
- 如果输入过短（< 50 字），摘要可以只有 1 句话

## 示例
输入："React 是一个用于构建用户界面的 JavaScript 库。它采用组件化的开发方式，通过虚拟 DOM 提高渲染性能。React 由 Facebook 开发和维护，是目前最流行的前端框架之一。"
输出：{"summary":"React 是 Facebook 开发的 JavaScript 前端库，采用组件化和虚拟 DOM 实现高性能 UI 渲染，是目前最主流的前端框架。","keywords":["React","JavaScript","组件化","虚拟DOM","前端框架"]}`;
```

## 4. API 客户端封装

```typescript
// src/lib/ai-client.ts

interface AiClientConfig {
  provider: "gemini" | "deepseek" | "groq" | "ollama";
  apiKey?: string;
  baseUrl?: string;
}

interface ChatOptions {
  messages: { role: string; content: string }[];
  maxTokens?: number;
  temperature?: number;
  stream?: boolean;
  signal?: AbortSignal;
}

class AiClient {
  private config: AiClientConfig;

  constructor(config: AiClientConfig) {
    this.config = config;
  }

  async chat(options: ChatOptions): Promise<Response> {
    // 根据 provider 构建不同的请求
    switch (this.config.provider) {
      case "gemini":
        return this.chatGemini(options);
      case "deepseek":
      case "groq":
      case "ollama":
        return this.chatOpenAiCompatible(options);
    }
  }

  private async chatGemini(options: ChatOptions): Promise<Response> {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:streamGenerateContent?key=${this.config.apiKey}&alt=sse`;
    // 转换 messages 格式为 Gemini 格式
    // ...
  }

  private async chatOpenAiCompatible(options: ChatOptions): Promise<Response> {
    const url = `${this.config.baseUrl}/v1/chat/completions`;
    return fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify({
        model:
          this.config.provider === "deepseek"
            ? "deepseek-chat"
            : "llama-3.3-70b-versatile",
        messages: options.messages,
        max_tokens: options.maxTokens ?? 1024,
        temperature: options.temperature ?? 0.7,
        stream: options.stream ?? true,
      }),
      signal: options.signal,
    });
  }
}

// 工厂函数：根据环境变量自动选择 provider
export function createAiClient(): AiClient {
  const provider = import.meta.env.VITE_AI_PROVIDER || "gemini";
  const apiKey = import.meta.env.VITE_AI_API_KEY;
  const baseUrl = import.meta.env.VITE_AI_BASE_URL;
  return new AiClient({ provider: provider as any, apiKey, baseUrl });
}
```

## 5. Streaming 处理

```typescript
// src/hooks/useAiChat.ts 中的 streaming 处理

async function* streamChat(response: Response): AsyncGenerator<string> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        try {
          const parsed = JSON.parse(data);
          const content = extractContent(parsed); // 根据 provider 提取 delta 文本
          if (content) yield content;
        } catch {
          /* skip malformed chunks */
        }
      }
    }
  }
}
```

## 6. 错误处理

```typescript
type AiError =
  | { type: 'token_limit'; message: string }
  | { type: 'network'; message: string }
  | { type: 'api_error'; message: string; status?: number }
  | { type: 'rate_limit'; message: string; retryAfter?: number }
  | { type: 'timeout'; message: string };

// 在 UI 中友好展示
function ErrorDisplay({ error }: { error: AiError }) {
  switch (error.type) {
    case 'token_limit':
      return <div>⚠️ 输入过长，请精简后重试</div>;
    case 'rate_limit':
      return <div>⏳ 请求太频繁，请稍后再试</div>;
    case 'timeout':
      return <div>⏱️ AI 响应超时，请重试</div>;
    default:
      return <div>❌ {error.message}</div>;
  }
}
```

## 7. 环境变量

```bash
# .env（不提交到 Git）
VITE_AI_PROVIDER=gemini          # gemini | deepseek | groq | ollama
VITE_AI_API_KEY=your_key_here    # API Key
VITE_AI_BASE_URL=                # 仅 deepseek/groq/ollama 需要

# .env.example（提交到 Git）
VITE_AI_PROVIDER=gemini
VITE_AI_API_KEY=your_api_key_here
VITE_AI_BASE_URL=
```

## 8. AI 资讯速览数据管道

> 这个模块**不调用 AI API**，数据来自 `project/aiNews` 的离线产出。这里设计的是数据格式和同步脚本。

### 8.1 数据格式（`public/data/ainews.json`）

```json
{
  "lastUpdated": "2026-11-07",
  "days": [
    {
      "date": "2026-11-07",
      "summary": "今天收集到 12 条 AI 资讯，整体方向是...",
      "top3": [
        {
          "title": "Gemini 2.5 Pro 发布",
          "source": "Google DeepMind Blog",
          "link": "https://deepmind.google/...",
          "reason": "新一代旗舰模型，推理能力大幅提升"
        },
        {
          "title": "LangChain v0.4 发布",
          "source": "GitHub Trending",
          "link": "https://github.com/langchain-ai/...",
          "reason": "Agent 框架重大更新，影响广泛"
        },
        {
          "title": "OpenAI 开源新推理模型",
          "source": "OpenAI News",
          "link": "https://openai.com/news/...",
          "reason": "开源策略转变，社区反响强烈"
        }
      ]
    }
  ]
}
```

### 8.2 同步脚本（`scripts/sync-ainews.sh`）

每次 aiNews 跑完后，手动或自动执行此脚本，将最新产出合并到主页数据中：

```bash
#!/bin/bash
# scripts/sync-ainews.sh
# 用法: ./scripts/sync-ainews.sh
# 从 project/aiNews/ 的产出目录读取最新数据，更新 homepage/public/data/ainews.json

AI_NEWS_DIR="../aiNews"
OUTPUT_FILE="public/data/ainews.json"
TEMP_FILE=$(mktemp)

# 1. 读取已有的 ainews.json（如果存在）
if [ -f "$OUTPUT_FILE" ]; then
  EXISTING_DATES=$(jq -r '.days[].date' "$OUTPUT_FILE")
else
  EXISTING_DATES=""
fi

# 2. 扫描 aiNews 产出目录，找到所有日期目录
# 3. 对每个新日期，解析 00_summary.md 和 02_top3.md
# 4. 合并到 ainews.json（去重，保留最近 14 天）

echo "TODO: 实现具体合并逻辑"
# 实际实现时用 jq 或 Node.js 脚本处理 Markdown → JSON 转换
```

### 8.3 更简单的方案：手动维护 JSON

考虑到 aiNews 产出是 Markdown 格式，解析成本较高，**初期建议直接手动维护 `ainews.json`**：

1. 每次跑完 aiNews 后，打开 `02_top3.md` 和 `00_summary.md`
2. 手动把当天的 Top 3 和摘要追加到 `ainews.json` 的 `days` 数组头部
3. 更新 `lastUpdated` 字段
4. 保持最多 14 天数据，旧的删掉

> 后续可以写一个 Node.js 脚本自动化这一步，但初期手动更可控。

### 8.4 前端加载

```typescript
// src/hooks/useNewsData.ts
import { useState, useEffect } from "react";

interface NewsDay {
  date: string;
  summary: string;
  top3: { title: string; source: string; link: string; reason: string }[];
}

interface NewsData {
  lastUpdated: string;
  days: NewsDay[];
}

export function useNewsData() {
  const [data, setData] = useState<NewsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/data/ainews.json")
      .then((res) => {
        if (!res.ok) throw new Error("资讯数据加载失败");
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // 只展示最近 7 天
  const recentDays = data?.days.slice(0, 7) ?? [];

  return { data, recentDays, loading, error };
}
```
