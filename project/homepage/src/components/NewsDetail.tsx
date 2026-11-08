import type { NewsTop3Item } from "../hooks/useNewsData";

export function NewsDetail({ items }: { items: NewsTop3Item[] }) {
  if (items.length === 0) return null;
  return (
    <ul className="mt-2 space-y-2 border-t border-slate-200 pt-2 dark:border-slate-800">
      {items.map((item) => (
        <li key={item.link || item.title} className="text-sm">
          <a
            href={item.link}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
          >
            {item.title}
          </a>
          <span className="ml-2 text-xs text-slate-500 dark:text-slate-400">
            {item.source}
          </span>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {item.reason}
          </p>
        </li>
      ))}
    </ul>
  );
}
