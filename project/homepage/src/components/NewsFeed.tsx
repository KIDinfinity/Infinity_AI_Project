import { useNewsData } from "../hooks/useNewsData";
import { NewsList } from "./NewsList";
import { SITE_CONFIG } from "../site.config";

export function NewsFeed() {
  const { data, recentDays, loading, error } = useNewsData();

  return (
    <section className="mx-auto max-w-2xl px-4 py-12">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold">AI 资讯速览</h2>
        {data && (
          <span className="text-xs text-slate-500 dark:text-slate-400">
            最近更新：{data.lastUpdated}
          </span>
        )}
      </div>
      {loading && <p className="text-sm text-slate-500">加载中…</p>}
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}
      {!loading && !error && recentDays.length === 0 && (
        <p className="text-sm text-slate-500">
          暂无资讯数据，运行{" "}
          <code className="rounded bg-slate-100 px-1 dark:bg-slate-800">
            pnpm news:add
          </code>{" "}
          添加第一条
        </p>
      )}
      {recentDays.length > 0 && <NewsList days={recentDays} />}
      <p className="mt-4 text-center text-xs text-slate-400">
        数据来自{" "}
        <a
          href={SITE_CONFIG.links.github}
          target="_blank"
          rel="noreferrer"
          className="hover:underline"
        >
          每日 AI 资讯自动收集 →
        </a>
      </p>
    </section>
  );
}
