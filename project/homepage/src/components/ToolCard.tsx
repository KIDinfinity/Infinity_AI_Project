import { Link } from "react-router-dom";
import type { ToolMeta } from "../tools/registry";

export function ToolCard({ tool }: { tool: ToolMeta }) {
  const Icon = tool.icon;
  return (
    <Link
      to={`/tools/${tool.slug}`}
      className="flex flex-col gap-2 rounded-xl border border-slate-200 p-4 transition hover:border-slate-400 hover:shadow-sm dark:border-slate-800 dark:hover:border-slate-600"
    >
      <Icon size={20} />
      <span className="font-medium">{tool.name}</span>
      <span className="text-xs text-slate-500 dark:text-slate-400">
        {tool.description}
      </span>
    </Link>
  );
}
