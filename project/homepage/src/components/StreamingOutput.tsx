export function StreamingOutput({
  content,
  isLoading,
}: {
  content: string;
  isLoading: boolean;
}) {
  if (!content && !isLoading) return null;
  return (
    <div className="whitespace-pre-wrap rounded-lg bg-slate-50 px-4 py-3 text-sm leading-relaxed dark:bg-slate-900">
      {content}
      {isLoading && <span className="animate-pulse">▍</span>}
    </div>
  );
}
