import { CODE_MODE_OPTIONS, type CodeMode } from "../lib/code-modes";

export function LangSelect({
  value,
  onChange,
}: {
  value: CodeMode;
  onChange: (v: CodeMode) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as CodeMode)}
      className="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900"
    >
      {CODE_MODE_OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
