import { AI_CONFIG } from "../lib/constants";

export function TokenBadge({
  prompt,
  completion,
}: {
  prompt: number;
  completion: number;
}) {
  const total = prompt + completion;
  const overBudget = total > AI_CONFIG.MAX_TOTAL_TOKENS;
  return (
    <span
      className={`rounded-full px-2 py-0.5 font-mono text-xs ${
        overBudget
          ? "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
          : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
      }`}
    >
      {total}/{AI_CONFIG.MAX_TOTAL_TOKENS} tokens
    </span>
  );
}
