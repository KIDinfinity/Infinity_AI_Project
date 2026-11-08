import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { NewsDay } from "../hooks/useNewsData";
import { NewsDetail } from "./NewsDetail";

export function NewsList({ days }: { days: NewsDay[] }) {
  const [openDate, setOpenDate] = useState<string | null>(
    days[0]?.date ?? null,
  );

  return (
    <ul className="space-y-2">
      {days.map((day) => {
        const isOpen = openDate === day.date;
        return (
          <li
            key={day.date}
            className="rounded-xl border border-slate-200 p-4 dark:border-slate-800"
          >
            <button
              type="button"
              onClick={() => setOpenDate(isOpen ? null : day.date)}
              className="flex w-full items-center justify-between text-left"
            >
              <div>
                <p className="font-mono text-xs text-slate-500 dark:text-slate-400">
                  {day.date}
                </p>
                <p className="text-sm text-slate-700 dark:text-slate-300">
                  {day.summary}
                </p>
              </div>
              {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            {isOpen && <NewsDetail items={day.top3} />}
          </li>
        );
      })}
    </ul>
  );
}
