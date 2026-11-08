export function CodeInput({
  value,
  onChange,
  placeholder = "粘贴代码…",
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      rows={8}
      spellCheck={false}
      className="w-full resize-y rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 dark:border-slate-700 dark:bg-slate-900"
    />
  );
}
