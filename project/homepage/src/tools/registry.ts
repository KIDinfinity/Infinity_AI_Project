import type { LucideIcon } from "lucide-react";
import { Braces } from "lucide-react";
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
  // 新增工具只需在此数组追加一项，见 design/05_tools.md
];
