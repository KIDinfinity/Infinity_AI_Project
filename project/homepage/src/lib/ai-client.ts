import {
  AI_CONFIG,
  DEFAULT_MODELS,
  DEFAULT_BASE_URLS,
  type AiProvider,
} from "./constants";

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatOptions {
  messages: ChatMessage[];
  maxTokens?: number;
  temperature?: number;
  signal?: AbortSignal;
}

interface AiClientConfig {
  provider: AiProvider;
  apiKey?: string;
  baseUrl?: string;
  model: string;
}

export class AiConfigError extends Error {}

interface GeminiStreamChunk {
  candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
}

interface OpenAiStreamChunk {
  choices?: Array<{ delta?: { content?: string } }>;
}

function readEnvConfig(): AiClientConfig {
  const provider =
    (import.meta.env.VITE_AI_PROVIDER as AiProvider | undefined) ?? "gemini";
  const apiKey = import.meta.env.VITE_AI_API_KEY as string | undefined;
  const baseUrl =
    (import.meta.env.VITE_AI_BASE_URL as string | undefined) ||
    (provider === "gemini" ? undefined : DEFAULT_BASE_URLS[provider]);
  const model =
    (import.meta.env.VITE_AI_MODEL as string | undefined) ||
    DEFAULT_MODELS[provider];
  return { provider, apiKey, baseUrl, model };
}

export function isAiConfigured(): boolean {
  const { provider, apiKey, baseUrl } = readEnvConfig();
  if (provider === "ollama") return true; // 本地模型不需要 key
  return Boolean(apiKey) && (provider === "gemini" || Boolean(baseUrl));
}

class AiClient {
  private config: AiClientConfig;

  constructor(config: AiClientConfig) {
    this.config = config;
  }

  /** 流式对话，逐段 yield 文本 delta */
  async *streamChat(options: ChatOptions): AsyncGenerator<string> {
    if (this.config.provider === "gemini") {
      yield* this.streamGemini(options);
    } else {
      yield* this.streamOpenAiCompatible(options);
    }
  }

  /** 一次性对话，返回完整文本（用于要求 JSON 结构化输出的场景） */
  async chatOnce(options: ChatOptions): Promise<string> {
    let full = "";
    for await (const chunk of this.streamChat(options)) {
      full += chunk;
    }
    return full;
  }

  private splitMessages(messages: ChatMessage[]) {
    const system = messages.find((m) => m.role === "system")?.content ?? "";
    const rest = messages.filter((m) => m.role !== "system");
    return { system, rest };
  }

  private async *streamGemini(options: ChatOptions): AsyncGenerator<string> {
    const { apiKey, model } = this.config;
    if (!apiKey)
      throw new AiConfigError("AI 未配置：请在 .env 中设置 VITE_AI_API_KEY");
    const { system, rest } = this.splitMessages(options.messages);

    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?key=${apiKey}&alt=sse`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: options.signal,
      body: JSON.stringify({
        systemInstruction: system ? { parts: [{ text: system }] } : undefined,
        contents: rest.map((m) => ({
          role: m.role === "assistant" ? "model" : "user",
          parts: [{ text: m.content }],
        })),
        generationConfig: {
          maxOutputTokens: options.maxTokens ?? AI_CONFIG.MAX_OUTPUT_TOKENS,
          temperature: options.temperature ?? 0.7,
        },
      }),
    });

    if (!res.ok || !res.body) {
      throw new Error(`Gemini 请求失败：${res.status}`);
    }

    yield* this.readSse<GeminiStreamChunk>(
      res.body,
      (json) => json.candidates?.[0]?.content?.parts?.[0]?.text ?? "",
    );
  }

  private async *streamOpenAiCompatible(
    options: ChatOptions,
  ): AsyncGenerator<string> {
    const { apiKey, baseUrl, model, provider } = this.config;
    if (provider !== "ollama" && !apiKey) {
      throw new AiConfigError("AI 未配置：请在 .env 中设置 VITE_AI_API_KEY");
    }
    const url = `${(baseUrl ?? "").replace(/\/$/, "")}/v1/chat/completions`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}),
      },
      signal: options.signal,
      body: JSON.stringify({
        model,
        messages: options.messages,
        max_tokens: options.maxTokens ?? AI_CONFIG.MAX_OUTPUT_TOKENS,
        temperature: options.temperature ?? 0.7,
        stream: true,
      }),
    });

    if (!res.ok || !res.body) {
      throw new Error(`${provider} 请求失败：${res.status}`);
    }

    yield* this.readSse<OpenAiStreamChunk>(
      res.body,
      (json) => json.choices?.[0]?.delta?.content ?? "",
    );
  }

  private async *readSse<T>(
    body: ReadableStream<Uint8Array>,
    extract: (json: T) => string,
  ): AsyncGenerator<string> {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;
        const data = trimmed.slice(5).trim();
        if (data === "[DONE]") return;
        try {
          const json = JSON.parse(data) as T;
          const text = extract(json);
          if (text) yield text;
        } catch {
          // 跳过无法解析的分片
        }
      }
    }
  }
}

export function createAiClient(): AiClient {
  return new AiClient(readEnvConfig());
}
