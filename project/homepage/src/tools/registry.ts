import type { LucideIcon } from "lucide-react";
import { Braces, LineChart } from "lucide-react";
import { lazy, type LazyExoticComponent, type ComponentType } from "react";

export type ToolCategory = "dev" | "text" | "convert" | "ai-enhanced" | "misc";

export interface ToolMeta {
  slug: string;
  name: string;
  description: string;
  category: ToolCategory;
  icon: LucideIcon;
  usesAi: boolean;
  featured?: boolean;
  component: LazyExoticComponent<ComponentType>;
}

export const TOOLS_REGISTRY: ToolMeta[] = [
  {
    slug: "json-formatter",
    name: "JSON 格式化 / 校验",
    description: "粘贴 JSON，自动格式化、校验语法、一键压缩",
    category: "dev",
    icon: Braces,
    usesAi: false,
    featured: true,
    component: lazy(() => import("./json-formatter")),
  },
  {
    slug: "function-graph",
    name: "函数图像展示器",
    description: "一次/二次/指数/对数/反比例/分段函数，描述函数并实时查看图像",
    category: "misc",
    icon: LineChart,
    usesAi: false,
    featured: true,
    component: lazy(() => import("./function-graph")),
  },
  // 新增工具只需在此数组追加一项，见 design/05_tools.md
];
