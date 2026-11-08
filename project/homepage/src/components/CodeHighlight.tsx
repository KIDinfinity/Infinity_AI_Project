export function CodeHighlight({ code }: { code: string }) {
  return (
    <pre className="overflow-x-auto rounded-lg bg-slate-900 px-4 py-3 text-xs text-slate-100">
      <code>{code}</code>
    </pre>
  );
}
