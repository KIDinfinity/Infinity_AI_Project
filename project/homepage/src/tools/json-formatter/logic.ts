export interface FormatResult {
  formatted: string | null;
  error: string | null;
}

export function formatJson(input: string, indent = 2): FormatResult {
  if (!input.trim()) return { formatted: null, error: null };
  try {
    const parsed: unknown = JSON.parse(input);
    return { formatted: JSON.stringify(parsed, null, indent), error: null };
  } catch (err) {
    return { formatted: null, error: (err as Error).message };
  }
}

export function minifyJson(input: string): FormatResult {
  if (!input.trim()) return { formatted: null, error: null };
  try {
    const parsed: unknown = JSON.parse(input);
    return { formatted: JSON.stringify(parsed), error: null };
  } catch (err) {
    return { formatted: null, error: (err as Error).message };
  }
}
