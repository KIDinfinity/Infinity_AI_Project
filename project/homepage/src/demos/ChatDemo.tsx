import { useAiChat } from "../hooks/useAiChat";
import { CHAT_SYSTEM_PROMPT } from "../lib/prompts";
import { ChatInput } from "../components/ChatInput";
import { StreamingOutput } from "../components/StreamingOutput";
import { QuickQuestions } from "../components/QuickQuestions";
import { TokenBadge } from "../components/TokenBadge";
import { LoadingSpinner } from "../components/LoadingSpinner";

const QUICK_QUESTIONS = [
  "你擅长什么技术？",
  "RAG 是什么？",
  "这个网站是怎么做的？",
];

export function ChatDemo() {
  const { messages, isLoading, error, tokenUsage, configured, sendMessage } =
    useAiChat({
      systemPrompt: CHAT_SYSTEM_PROMPT,
    });

  const lastAssistant = [...messages]
    .reverse()
    .find((m) => m.role === "assistant");

  return (
    <div className="space-y-3">
      {!configured && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300">
          AI 未配置：请在 .env 中设置 VITE_AI_API_KEY 后体验此 Demo
        </p>
      )}
      <QuickQuestions
        questions={QUICK_QUESTIONS}
        onPick={sendMessage}
        disabled={isLoading || !configured}
      />
      {isLoading && !lastAssistant?.content && <LoadingSpinner />}
      {lastAssistant && (
        <StreamingOutput
          content={lastAssistant.content}
          isLoading={isLoading}
        />
      )}
      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
      )}
      <ChatInput onSend={sendMessage} disabled={isLoading || !configured} />
      <div className="flex justify-end">
        <TokenBadge
          prompt={tokenUsage.prompt}
          completion={tokenUsage.completion}
        />
      </div>
    </div>
  );
}
