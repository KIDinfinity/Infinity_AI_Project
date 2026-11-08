export const AI_CONFIG = {
  MAX_INPUT_TOKENS: 1500,
  MAX_OUTPUT_TOKENS: 1024,
  MAX_TOTAL_TOKENS: 2048,
  TRUNCATE_WARNING: 1200,
} as const;

export type AiProvider = "gemini" | "deepseek" | "groq" | "ollama";

export const DEFAULT_MODELS: Record<AiProvider, string> = {
  gemini: "gemini-2.0-flash-001",
  deepseek: "deepseek-chat",
  groq: "llama-3.3-70b-versatile",
  ollama: "qwen2.5:3b",
};

export const DEFAULT_BASE_URLS: Record<
  Exclude<AiProvider, "gemini">,
  string
> = {
  deepseek: "https://api.deepseek.com",
  groq: "https://api.groq.com/openai",
  ollama: "http://localhost:11434",
};
