import type { ToolCategory } from "../tools/registry";

const LABELS: Record<ToolCategory | "all", string> = {
  all: "全部",
  dev: "开发",
  text: "文本",
  convert: "转换",
  "ai-enhanced": "AI 增强",
  misc: "其他",
};

export function CategoryFilter({
  value,
  onChange,
}: {
  value: ToolCategory | "all";
  onChange: (v: ToolCategory | "all") => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {(Object.keys(LABELS) as Array<ToolCategory | "all">).map((key) => (
        <button
          key={key}
          type="button"
          onClick={() => onChange(key)}
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            value === key
              ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
          }`}
        >
          {LABELS[key]}
        </button>
      ))}
    </div>
  );
}
