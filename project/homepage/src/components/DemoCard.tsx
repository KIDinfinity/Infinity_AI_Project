import type { ReactNode } from "react";

export function DemoCard({
  title,
  description,
  tags,
  children,
}: {
  title: string;
  description: string;
  tags: string[];
  children: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
        {description}
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {tags.map((tag) => (
          <span
            key={tag}
            className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
          >
            {tag}
          </span>
        ))}
      </div>
      <div className="mt-4 space-y-3">{children}</div>
    </div>
  );
}
