import { Suspense } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { TOOLS_REGISTRY } from "../tools/registry";
import { LoadingSpinner } from "../components/LoadingSpinner";

export function ToolDetailPage() {
  const { slug } = useParams();
  const meta = TOOLS_REGISTRY.find((t) => t.slug === slug);

  if (!meta) {
    return (
      <section className="mx-auto max-w-xl px-4 py-16 text-center">
        <p className="text-slate-600 dark:text-slate-400">工具不存在</p>
        <Link
          to="/tools"
          className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          返回工具箱 →
        </Link>
      </section>
    );
  }

  const ToolComponent = meta.component;

  return (
    <section className="mx-auto max-w-2xl px-4 py-12">
      <Link
        to="/tools"
        className="mb-6 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
      >
        <ArrowLeft size={14} /> 返回工具箱
      </Link>
      <h1 className="mb-1 text-2xl font-bold">{meta.name}</h1>
      <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
        {meta.description}
      </p>
      <Suspense fallback={<LoadingSpinner label="工具加载中…" />}>
        <ToolComponent />
      </Suspense>
    </section>
  );
}
