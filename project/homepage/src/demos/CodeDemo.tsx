import { useState } from "react";
import { useAiJson } from "../hooks/useAiJson";
import { CODE_SYSTEM_PROMPT } from "../lib/prompts";
import { CodeInput } from "../components/CodeInput";
import { LangSelect } from "../components/LangSelect";
import { type CodeMode } from "../lib/code-modes";
import { CodeHighlight } from "../components/CodeHighlight";
import { LoadingSpinner } from "../components/LoadingSpinner";

interface CodeResult {
  explanation: string;
  code: string | null;
}

export function CodeDemo() {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<CodeMode>("explain");
  const { result, isLoading, error, configured, run } =
    useAiJson<CodeResult>(CODE_SYSTEM_PROMPT);

  const handleSubmit = () => {
    if (!input.trim()) return;
    run(`模式: ${mode}\n代码:\n${input}`);
  };

  return (
    <div className="space-y-3">
      {!configured && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-300">
          AI 未配置：请在 .env 中设置 VITE_AI_API_KEY 后体验此 Demo
        </p>
      )}
      <CodeInput value={input} onChange={setInput} />
      <div className="flex items-center gap-2">
        <LangSelect value={mode} onChange={setMode} />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={isLoading || !configured || !input.trim()}
          className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white disabled:opacity-40 dark:bg-slate-100 dark:text-slate-900"
        >
          提交
        </button>
      </div>
      {isLoading && <LoadingSpinner />}
      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">{error}</p>
      )}
      {result && (
        <div className="space-y-2">
          <p className="text-sm text-slate-700 dark:text-slate-300">
            {result.explanation}
          </p>
          {result.code && <CodeHighlight code={result.code} />}
        </div>
      )}
    </div>
  );
}
