import { useState } from "react";
import { TOOLS_REGISTRY, type ToolCategory } from "../tools/registry";
import { ToolCard } from "../components/ToolCard";
import { CategoryFilter } from "../components/CategoryFilter";

export function ToolsIndexPage() {
  const [category, setCategory] = useState<ToolCategory | "all">("all");
  const tools =
    category === "all"
      ? TOOLS_REGISTRY
      : TOOLS_REGISTRY.filter((t) => t.category === category);

  return (
    <section className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="mb-2 text-center text-3xl font-bold">工具箱</h1>
      <p className="mb-6 text-center text-sm text-slate-500 dark:text-slate-400">
        免费、即开即用的小工具，持续新增
      </p>
      <div className="mb-6 flex justify-center">
        <CategoryFilter value={category} onChange={setCategory} />
      </div>
      {tools.length === 0 ? (
        <p className="text-center text-sm text-slate-500">该分类下暂无工具</p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {tools.map((tool) => (
            <ToolCard key={tool.slug} tool={tool} />
          ))}
        </div>
      )}
    </section>
  );
}
