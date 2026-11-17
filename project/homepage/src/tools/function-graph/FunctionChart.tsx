import type { PlotPoint } from "./logic";

interface FunctionChartProps {
  points: PlotPoint[];
  xDomain: [number, number];
  yDomain: [number, number];
}

const WIDTH = 320;
const HEIGHT = 320;
const PADDING = 24;

export function FunctionChart({
  points,
  xDomain,
  yDomain,
}: FunctionChartProps) {
  const [xMin, xMax] = xDomain;
  const [yMin, yMax] = yDomain;

  const toPx = (x: number) =>
    PADDING + ((x - xMin) / (xMax - xMin)) * (WIDTH - PADDING * 2);
  const toPy = (y: number) =>
    HEIGHT - PADDING - ((y - yMin) / (yMax - yMin)) * (HEIGHT - PADDING * 2);

  const segments: string[] = [];
  let current = "";
  for (const p of points) {
    if (p.y === null) {
      if (current) {
        segments.push(current);
        current = "";
      }
      continue;
    }
    const px = toPx(p.x);
    const py = toPy(p.y);
    current += current ? ` L ${px} ${py}` : `M ${px} ${py}`;
  }
  if (current) segments.push(current);

  const showXAxis = yMin < 0 && yMax > 0;
  const showYAxis = xMin < 0 && xMax > 0;

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label="函数图像"
      className="w-full max-w-sm rounded-lg border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
    >
      <rect
        x={PADDING}
        y={PADDING}
        width={WIDTH - PADDING * 2}
        height={HEIGHT - PADDING * 2}
        fill="none"
        className="stroke-slate-200 dark:stroke-slate-700"
      />
      {showXAxis && (
        <line
          x1={PADDING}
          y1={toPy(0)}
          x2={WIDTH - PADDING}
          y2={toPy(0)}
          strokeWidth={1}
          className="stroke-slate-400 dark:stroke-slate-500"
        />
      )}
      {showYAxis && (
        <line
          x1={toPx(0)}
          y1={PADDING}
          x2={toPx(0)}
          y2={HEIGHT - PADDING}
          strokeWidth={1}
          className="stroke-slate-400 dark:stroke-slate-500"
        />
      )}
      {segments.map((d, i) => (
        <path
          key={i}
          d={d}
          fill="none"
          strokeWidth={2}
          className="stroke-indigo-600 dark:stroke-indigo-400"
        />
      ))}
    </svg>
  );
}
