import { useCallback, useRef, useState } from "react";
import {
  createAiClient,
  isAiConfigured,
  AiConfigError,
  type ChatMessage,
} from "../lib/ai-client";
import { countTokens, truncateByTokens } from "../lib/tokenizer";
import { AI_CONFIG } from "../lib/constants";

export interface UseAiChatOptions {
  systemPrompt: string;
}

export type ChatRole = "user" | "assistant";
export interface ChatTurn {
  role: ChatRole;
  content: string;
}

export function useAiChat({ systemPrompt }: UseAiChatOptions) {
  const [messages, setMessages] = useState<ChatTurn[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tokenUsage, setTokenUsage] = useState({ prompt: 0, completion: 0 });
  const abortRef = useRef<AbortController | null>(null);
  const configured = isAiConfigured();

  const sendMessage = useCallback(
    async (rawInput: string) => {
      if (!configured) {
        setError("AI 未配置：请在 .env 中设置 VITE_AI_API_KEY 后重试");
        return;
      }
      setError(null);
      let input = rawInput;
      const systemTokens = countTokens(systemPrompt);
      const inputTokens = countTokens(input);

      if (systemTokens + inputTokens > AI_CONFIG.MAX_INPUT_TOKENS) {
        const budget = Math.max(AI_CONFIG.MAX_INPUT_TOKENS - systemTokens, 100);
        input = truncateByTokens(input, budget);
        setError("输入过长，已自动截断");
      }

      const userTurn: ChatTurn = { role: "user", content: input };
      setMessages((prev) => [
        ...prev,
        userTurn,
        { role: "assistant", content: "" },
      ]);
      setIsLoading(true);
      setTokenUsage({
        prompt: systemTokens + countTokens(input),
        completion: 0,
      });

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const client = createAiClient();
        const history = [...messages, userTurn];
        const chatMessages: ChatMessage[] = [
          { role: "system", content: systemPrompt },
          ...history.map((m) => ({ role: m.role, content: m.content })),
        ];

        let assistantText = "";
        for await (const chunk of client.streamChat({
          messages: chatMessages,
          maxTokens: AI_CONFIG.MAX_OUTPUT_TOKENS,
          signal: controller.signal,
        })) {
          assistantText += chunk;
          setMessages((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = {
              role: "assistant",
              content: assistantText,
            };
            return copy;
          });
          setTokenUsage((prev) => ({
            ...prev,
            completion: countTokens(assistantText),
          }));
        }
      } catch (err) {
        if (err instanceof AiConfigError) {
          setError(err.message);
        } else if (err instanceof DOMException && err.name === "AbortError") {
          // 用户主动取消，不展示错误
        } else {
          setError("AI 响应失败，请稍后重试");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [messages, systemPrompt, configured],
  );

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setError(null);
    setTokenUsage({ prompt: 0, completion: 0 });
  }, []);

  return {
    messages,
    isLoading,
    error,
    tokenUsage,
    configured,
    sendMessage,
    reset,
  };
}
