import { Link } from "react-router-dom";
import { TOOLS_REGISTRY } from "../tools/registry";
import { ToolCard } from "./ToolCard";

export function ToolboxPreview() {
  const featured = TOOLS_REGISTRY.filter((t) => t.featured).slice(0, 6);

  return (
    <section className="mx-auto max-w-2xl px-4 py-12">
      <h2 className="mb-6 text-center text-2xl font-bold">工具箱</h2>
      {featured.length === 0 ? (
        <p className="text-center text-sm text-slate-500">
          工具箱筹备中，敬请期待
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {featured.map((tool) => (
            <ToolCard key={tool.slug} tool={tool} />
          ))}
        </div>
      )}
      <div className="mt-4 text-center">
        <Link
          to="/tools"
          className="text-sm font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          查看全部工具 →
        </Link>
      </div>
    </section>
  );
}
