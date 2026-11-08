import { useState } from "react";
import { formatJson, minifyJson } from "./logic";

export default function JsonFormatterTool() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleFormat = () => {
    const { formatted, error: err } = formatJson(input);
    setOutput(formatted ?? "");
    setError(err);
  };

  const handleMinify = () => {
    const { formatted, error: err } = minifyJson(input);
    setOutput(formatted ?? "");
    setError(err);
  };

  return (
    <div className="space-y-3">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder='粘贴 JSON，例如 {"a": 1}'
        rows={8}
        spellCheck={false}
        className="w-full resize-y rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 font-mono text-sm dark:border-slate-700 dark:bg-slate-900"
      />
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleFormat}
          className="rounded-lg bg-slate-900 px-3 py-1.5 text-sm text-white dark:bg-slate-100 dark:text-slate-900"
        >
          格式化
        </button>
        <button
          type="button"
          onClick={handleMinify}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700"
        >
          压缩
        </button>
      </div>
      {error && (
        <p className="text-xs text-red-600 dark:text-red-400">
          JSON 无效：{error}
        </p>
      )}
      {output && (
        <pre className="overflow-x-auto rounded-lg bg-slate-900 px-4 py-3 text-xs text-slate-100">
          <code>{output}</code>
        </pre>
      )}
    </div>
  );
}
