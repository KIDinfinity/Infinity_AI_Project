export type FunctionType =
  | "linear"
  | "quadratic"
  | "exponential"
  | "logarithmic"
  | "inverse"
  | "piecewise";

export interface FunctionTypeOption {
  type: FunctionType;
  label: string;
}

export const FUNCTION_TYPE_OPTIONS: FunctionTypeOption[] = [
  { type: "linear", label: "一元一次函数 y = kx + b" },
  { type: "quadratic", label: "一元二次函数 y = ax² + bx + c" },
  { type: "exponential", label: "指数函数 y = a·bˣ" },
  { type: "logarithmic", label: "对数函数 y = a·log_b(x)" },
  { type: "inverse", label: "反比例函数 y = k / x" },
  { type: "piecewise", label: "分段函数（多段一次函数）" },
];

export interface LinearParams {
  k: number;
  b: number;
}

export interface QuadraticParams {
  a: number;
  b: number;
  c: number;
}

export interface ExponentialParams {
  a: number;
  base: number;
}

export interface LogarithmicParams {
  a: number;
  base: number;
}

export interface InverseParams {
  k: number;
}

export interface PiecewisePiece {
  id: string;
  from: number;
  to: number;
  k: number;
  b: number;
}

export interface PiecewiseParams {
  pieces: PiecewisePiece[];
}

export type FunctionParams =
  | { type: "linear"; params: LinearParams }
  | { type: "quadratic"; params: QuadraticParams }
  | { type: "exponential"; params: ExponentialParams }
  | { type: "logarithmic"; params: LogarithmicParams }
  | { type: "inverse"; params: InverseParams }
  | { type: "piecewise"; params: PiecewiseParams };

export interface AllDefaultParams {
  linear: LinearParams;
  quadratic: QuadraticParams;
  exponential: ExponentialParams;
  logarithmic: LogarithmicParams;
  inverse: InverseParams;
  piecewise: PiecewiseParams;
}

export const DEFAULT_PARAMS: AllDefaultParams = {
  linear: { k: 1, b: 0 },
  quadratic: { a: 1, b: 0, c: 0 },
  exponential: { a: 1, base: 2 },
  logarithmic: { a: 1, base: 2 },
  inverse: { k: 1 },
  piecewise: {
    pieces: [
      { id: "p1", from: -8, to: 0, k: -1, b: 0 },
      { id: "p2", from: 0, to: 8, k: 1, b: 0 },
    ],
  },
};

export const DEFAULT_DOMAIN: Record<FunctionType, [number, number]> = {
  linear: [-10, 10],
  quadratic: [-10, 10],
  exponential: [-5, 5],
  logarithmic: [0.1, 10],
  inverse: [-10, 10],
  piecewise: [-10, 10],
};

/** 对函数在某一点求值；定义域外或无意义时返回 null */
export function evaluate(func: FunctionParams, x: number): number | null {
  switch (func.type) {
    case "linear": {
      const { k, b } = func.params;
      return k * x + b;
    }
    case "quadratic": {
      const { a, b, c } = func.params;
      return a * x * x + b * x + c;
    }
    case "exponential": {
      const { a, base } = func.params;
      if (base <= 0 || base === 1) return null;
      return a * Math.pow(base, x);
    }
    case "logarithmic": {
      const { a, base } = func.params;
      if (x <= 0 || base <= 0 || base === 1) return null;
      return (a * Math.log(x)) / Math.log(base);
    }
    case "inverse": {
      const { k } = func.params;
      if (x === 0 || k === 0) return null;
      return k / x;
    }
    case "piecewise": {
      const piece = func.params.pieces.find((p) => x >= p.from && x < p.to);
      if (!piece) return null;
      return piece.k * x + piece.b;
    }
    default:
      return func;
  }
}

export interface PlotPoint {
  x: number;
  y: number | null;
}

/** 在 [xMin, xMax] 区间等间隔采样函数值 */
export function generatePoints(
  func: FunctionParams,
  xMin: number,
  xMax: number,
  numSamples = 400,
): PlotPoint[] {
  const points: PlotPoint[] = [];
  const step = (xMax - xMin) / numSamples;
  for (let i = 0; i <= numSamples; i++) {
    const x = xMin + i * step;
    const rawY = evaluate(func, x);
    const y = rawY !== null && Number.isFinite(rawY) ? rawY : null;
    points.push({ x, y });
  }
  return points;
}

/** 根据采样点自动计算一个适合展示的 y 轴范围，剔除渐近线附近的极端值 */
export function computeYDomain(points: PlotPoint[]): [number, number] {
  const values = points
    .map((p) => p.y)
    .filter((y): y is number => y !== null && Number.isFinite(y));

  if (values.length === 0) return [-10, 10];

  const sorted = [...values].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  const scale = Math.max(Math.abs(median), 1);
  const filtered = values.filter((v) => Math.abs(v) <= scale * 20);
  const pool = filtered.length > 0 ? filtered : values;

  let min = Math.min(...pool);
  let max = Math.max(...pool);
  if (min === max) {
    min -= 1;
    max += 1;
  }
  const padding = (max - min) * 0.1;
  return [min - padding, max + padding];
}

/** 把超出最终 y 轴范围的采样点置空，渐近线附近会形成断点 */
export function clipPointsToDomain(
  points: PlotPoint[],
  [yMin, yMax]: [number, number],
): PlotPoint[] {
  const margin = (yMax - yMin) * 0.05;
  return points.map((p) => {
    if (p.y === null) return p;
    if (p.y < yMin - margin || p.y > yMax + margin) {
      return { x: p.x, y: null };
    }
    return p;
  });
}

function formatNum(n: number): string {
  if (!Number.isFinite(n)) return String(n);
  return Number.isInteger(n) ? String(n) : n.toFixed(2).replace(/\.?0+$/, "");
}

function formatSigned(n: number): string {
  return `${n >= 0 ? "+" : "-"} ${formatNum(Math.abs(n))}`;
}

/** 生成函数的文字描述，用于「函数描述」区块展示 */
export function describeFunction(func: FunctionParams): string {
  switch (func.type) {
    case "linear": {
      const { k, b } = func.params;
      return `y = ${formatNum(k)}x ${formatSigned(b)}`;
    }
    case "quadratic": {
      const { a, b, c } = func.params;
      return `y = ${formatNum(a)}x² ${formatSigned(b)}x ${formatSigned(c)}`;
    }
    case "exponential": {
      const { a, base } = func.params;
      return `y = ${formatNum(a)} × ${formatNum(base)}^x`;
    }
    case "logarithmic": {
      const { a, base } = func.params;
      return `y = ${formatNum(a)} × log_${formatNum(base)}(x)（定义域 x > 0）`;
    }
    case "inverse": {
      const { k } = func.params;
      return `y = ${formatNum(k)} / x（x ≠ 0）`;
    }
    case "piecewise": {
      return func.params.pieces
        .map(
          (p) =>
            `[${formatNum(p.from)}, ${formatNum(p.to)}): y = ${formatNum(p.k)}x ${formatSigned(p.b)}`,
        )
        .join("；");
    }
    default:
      return func;
  }
}
