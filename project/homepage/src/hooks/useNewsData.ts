import { useEffect, useState } from "react";

export interface NewsTop3Item {
  title: string;
  source: string;
  link: string;
  reason: string;
}

export interface NewsDay {
  date: string;
  summary: string;
  top3: NewsTop3Item[];
}

export interface NewsData {
  lastUpdated: string;
  days: NewsDay[];
}

export function useNewsData() {
  const [data, setData] = useState<NewsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/ainews.json`)
      .then((res) => {
        if (!res.ok) throw new Error("资讯数据加载失败");
        return res.json() as Promise<NewsData>;
      })
      .then((json) => setData(json))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const recentDays = data?.days.slice(0, 7) ?? [];

  return { data, recentDays, loading, error };
}
