export const CODE_MODE_OPTIONS = [
  { value: "explain", label: "只解释" },
  { value: "python", label: "转 Python" },
  { value: "typescript", label: "转 TypeScript" },
  { value: "go", label: "转 Go" },
] as const;

export type CodeMode = (typeof CODE_MODE_OPTIONS)[number]["value"];
