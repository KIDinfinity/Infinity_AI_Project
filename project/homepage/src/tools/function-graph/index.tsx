import { useMemo, useState } from "react";
import {
  FUNCTION_TYPE_OPTIONS,
  DEFAULT_PARAMS,
  DEFAULT_DOMAIN,
  describeFunction,
  generatePoints,
  computeYDomain,
  clipPointsToDomain,
  type FunctionType,
  type FunctionParams,
  type AllDefaultParams,
  type LinearParams,
  type QuadraticParams,
  type ExponentialParams,
  type LogarithmicParams,
  type InverseParams,
  type PiecewisePiece,
} from "./logic";
import { FunctionChart } from "./FunctionChart";

let pieceIdCounter = 0;
function nextPieceId() {
  pieceIdCounter += 1;
  return `piece-${pieceIdCounter}`;
}

function NumberField({
  label,
  value,
  onChange,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: number;
}) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="w-16 shrink-0 text-slate-600 dark:text-slate-400">
        {label}
      </span>
      <input
        type="number"
        value={value}
        step={step}
        onChange={(e) => {
          const next = Number(e.target.value);
          if (!Number.isNaN(next)) onChange(next);
        }}
        className="w-full rounded-lg border border-slate-300 bg-slate-50 px-2 py-1 dark:border-slate-700 dark:bg-slate-900"
      />
    </label>
  );
}

export default function FunctionGraphTool() {
  const [type, setType] = useState<FunctionType>("linear");
  const [paramsState, setParamsState] = useState<AllDefaultParams>(() =>
    structuredClone(DEFAULT_PARAMS),
  );

  const setLinear = (patch: Partial<LinearParams>) =>
    setParamsState((prev) => ({
      ...prev,
      linear: { ...prev.linear, ...patch },
    }));
  const setQuadratic = (patch: Partial<QuadraticParams>) =>
    setParamsState((prev) => ({
      ...prev,
      quadratic: { ...prev.quadratic, ...patch },
    }));
  const setExponential = (patch: Partial<ExponentialParams>) =>
    setParamsState((prev) => ({
      ...prev,
      exponential: { ...prev.exponential, ...patch },
    }));
  const setLogarithmic = (patch: Partial<LogarithmicParams>) =>
    setParamsState((prev) => ({
      ...prev,
      logarithmic: { ...prev.logarithmic, ...patch },
    }));
  const setInverse = (patch: Partial<InverseParams>) =>
    setParamsState((prev) => ({
      ...prev,
      inverse: { ...prev.inverse, ...patch },
    }));

  const addPiece = () =>
    setParamsState((prev) => {
      const pieces = prev.piecewise.pieces;
      const lastTo = pieces.length > 0 ? pieces[pieces.length - 1].to : 0;
      return {
        ...prev,
        piecewise: {
          pieces: [
            ...pieces,
            { id: nextPieceId(), from: lastTo, to: lastTo + 5, k: 1, b: 0 },
          ],
        },
      };
    });

  const removePiece = (id: string) =>
    setParamsState((prev) => ({
      ...prev,
      piecewise: { pieces: prev.piecewise.pieces.filter((p) => p.id !== id) },
    }));

  const updatePiece = (id: string, patch: Partial<PiecewisePiece>) =>
    setParamsState((prev) => ({
      ...prev,
      piecewise: {
        pieces: prev.piecewise.pieces.map((p) =>
          p.id === id ? { ...p, ...patch } : p,
        ),
      },
    }));

  const func = useMemo<FunctionParams>(() => {
    switch (type) {
      case "linear":
        return { type, params: paramsState.linear };
      case "quadratic":
        return { type, params: paramsState.quadratic };
      case "exponential":
        return { type, params: paramsState.exponential };
      case "logarithmic":
        return { type, params: paramsState.logarithmic };
      case "inverse":
        return { type, params: paramsState.inverse };
      case "piecewise":
        return { type, params: paramsState.piecewise };
      default:
        return type;
    }
  }, [type, paramsState]);

  const [xMin, xMax] = DEFAULT_DOMAIN[type];

  const { points, yDomain } = useMemo(() => {
    const raw = generatePoints(func, xMin, xMax);
    const domain = computeYDomain(raw);
    const clipped = clipPointsToDomain(raw, domain);
    return { points: clipped, yDomain: domain };
  }, [func, xMin, xMax]);

  const renderParamFields = () => {
    switch (type) {
      case "linear":
        return (
          <>
            <NumberField
              label="斜率 k"
              value={paramsState.linear.k}
              onChange={(v) => setLinear({ k: v })}
            />
            <NumberField
              label="截距 b"
              value={paramsState.linear.b}
              onChange={(v) => setLinear({ b: v })}
            />
          </>
        );
      case "quadratic":
        return (
          <>
            <NumberField
              label="二次项 a"
              value={paramsState.quadratic.a}
              onChange={(v) => setQuadratic({ a: v })}
            />
            <NumberField
              label="一次项 b"
              value={paramsState.quadratic.b}
              onChange={(v) => setQuadratic({ b: v })}
            />
            <NumberField
              label="常数 c"
              value={paramsState.quadratic.c}
              onChange={(v) => setQuadratic({ c: v })}
            />
          </>
        );
      case "exponential":
        return (
          <>
            <NumberField
              label="系数 a"
              value={paramsState.exponential.a}
              onChange={(v) => setExponential({ a: v })}
            />
            <NumberField
              label="底数 b"
              value={paramsState.exponential.base}
              step={0.1}
              onChange={(v) => setExponential({ base: v })}
            />
          </>
        );
      case "logarithmic":
        return (
          <>
            <NumberField
              label="系数 a"
              value={paramsState.logarithmic.a}
              onChange={(v) => setLogarithmic({ a: v })}
            />
            <NumberField
              label="底数 b"
              value={paramsState.logarithmic.base}
              step={0.1}
              onChange={(v) => setLogarithmic({ base: v })}
            />
          </>
        );
      case "inverse":
        return (
          <NumberField
            label="系数 k"
            value={paramsState.inverse.k}
            onChange={(v) => setInverse({ k: v })}
          />
        );
      case "piecewise":
        return (
          <div className="space-y-2">
            {paramsState.piecewise.pieces.map((piece) => (
              <div
                key={piece.id}
                className="grid grid-cols-2 gap-2 rounded-lg border border-slate-200 p-2 dark:border-slate-700 sm:grid-cols-5 sm:items-center"
              >
                <NumberField
                  label="起点"
                  value={piece.from}
                  onChange={(v) => updatePiece(piece.id, { from: v })}
                />
                <NumberField
                  label="终点"
                  value={piece.to}
                  onChange={(v) => updatePiece(piece.id, { to: v })}
                />
                <NumberField
                  label="斜率 k"
                  value={piece.k}
                  onChange={(v) => updatePiece(piece.id, { k: v })}
                />
                <NumberField
                  label="截距 b"
                  value={piece.b}
                  onChange={(v) => updatePiece(piece.id, { b: v })}
                />
                <button
                  type="button"
                  onClick={() => removePiece(piece.id)}
                  disabled={paramsState.piecewise.pieces.length <= 1}
                  className="rounded-lg border border-slate-300 px-2 py-1 text-xs text-red-600 disabled:opacity-40 dark:border-slate-700"
                >
                  删除
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={addPiece}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700"
            >
              + 添加分段
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          1. 函数描述
        </h2>
        <select
          value={type}
          onChange={(e) => setType(e.target.value as FunctionType)}
          className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
        >
          {FUNCTION_TYPE_OPTIONS.map((opt) => (
            <option key={opt.type} value={opt.type}>
              {opt.label}
            </option>
          ))}
        </select>
        <div className="space-y-2">{renderParamFields()}</div>
        <p className="rounded-lg bg-slate-100 px-3 py-2 font-mono text-sm dark:bg-slate-800">
          {describeFunction(func)}
        </p>
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          2. 函数图像
        </h2>
        <FunctionChart
          points={points}
          xDomain={[xMin, xMax]}
          yDomain={yDomain}
        />
        <p className="text-xs text-slate-500 dark:text-slate-400">
          定义域外或趋于无穷的部分不绘制，渐近线附近会出现断点。
        </p>
      </section>
    </div>
  );
}
