import { useCallback, useState } from "react";
import {
  createAiClient,
  isAiConfigured,
  AiConfigError,
} from "../lib/ai-client";
import { countTokens, truncateByTokens } from "../lib/tokenizer";
import { AI_CONFIG } from "../lib/constants";

/** 一次性对话，要求 AI 返回 JSON 结构化结果（用于 CodeDemo / SummaryDemo） */
export function useAiJson<T>(systemPrompt: string) {
  const [result, setResult] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const configured = isAiConfigured();

  const run = useCallback(
    async (userInput: string) => {
      if (!configured) {
        setError("AI 未配置：请在 .env 中设置 VITE_AI_API_KEY 后重试");
        return;
      }
      setError(null);
      setResult(null);
      setIsLoading(true);

      let input = userInput;
      const systemTokens = countTokens(systemPrompt);
      if (systemTokens + countTokens(input) > AI_CONFIG.MAX_INPUT_TOKENS) {
        input = truncateByTokens(
          input,
          Math.max(AI_CONFIG.MAX_INPUT_TOKENS - systemTokens, 100),
        );
      }

      try {
        const client = createAiClient();
        const raw = await client.chatOnce({
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: input },
          ],
          maxTokens: AI_CONFIG.MAX_OUTPUT_TOKENS,
        });
        const cleaned = raw
          .trim()
          .replace(/^```json\s*/i, "")
          .replace(/^```\s*/, "")
          .replace(/```$/, "");
        setResult(JSON.parse(cleaned) as T);
      } catch (err) {
        if (err instanceof AiConfigError) {
          setError(err.message);
        } else if (err instanceof SyntaxError) {
          setError("AI 返回格式异常，请重试");
        } else {
          setError("AI 响应失败，请稍后重试");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [systemPrompt, configured],
  );

  return { result, isLoading, error, configured, run };
}
