import { useState } from "react";
import { useAiJson } from "../hooks/useAiJson";
import { SUMMARY_SYSTEM_PROMPT } from "../lib/prompts";
import { LoadingSpinner } from "../components/LoadingSpinner";

interface SummaryResult {
  summary: string;
  keywords: string[];
}

export function SummaryDemo() {
  const [input, setInput] = useState("");
  const { result, isLoading, error, configured, run } =
    useAiJson<SummaryResult>(SUMMARY_SYSTEM_PROMPT);

  return (
    <div className="space-y-3">
      {!configured && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300">
          AI 未配置：请在 .env 中设置 VITE_AI_API_KEY 后体验此 Demo
        </p>
      )}
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="粘贴一段长文本…"
        rows={6}
        className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 dark:border-slate-700 dark:bg-slate-900"
      />
      <button
        type="button"
        onClick={() => input.trim() && run(input)}
        disabled={isLoading || !configured || !input.trim()}
        className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-40 dark:bg-slate-100 dark:text-slate-900"
      >
        生成摘要
      </button>
      {isLoading && <LoadingSpinner />}
      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
      )}
      {result && (
        <div className="space-y-2 rounded-lg bg-slate-50 px-4 py-3 dark:bg-slate-900">
          <p className="text-sm">{result.summary}</p>
          <div className="flex flex-wrap gap-1.5">
            {result.keywords.map((k) => (
              <span
                key={k}
                className="rounded-full bg-slate-200 px-2 py-0.5 text-xs dark:bg-slate-800"
              >
                {k}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
