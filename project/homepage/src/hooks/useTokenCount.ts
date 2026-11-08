import { useMemo } from "react";
import { countTokens } from "../lib/tokenizer";

export function useTokenCount(text: string): number {
  return useMemo(() => countTokens(text), [text]);
}
