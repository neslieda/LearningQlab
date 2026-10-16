/** Same rule as the server (apps/api/src/qlab/content/schema/language.py): letters that occur in Turkish and not in English. */
export const NON_ENGLISH_LETTERS = "ğĞıİşŞ";

/**
 * Paths (like `content[0].content[1].text`, or `mcq.options[1].rationale` when given a whole question
 * document) of every string holding a Turkish-only letter. Walks any JSON value, as the server does.
 */
export function nonEnglishPaths(value: unknown, base = ""): string[] {
  const found: string[] = [];
  const walk = (v: unknown, path: string): void => {
    if (typeof v === "string") {
      if ([...v].some((ch) => NON_ENGLISH_LETTERS.includes(ch))) found.push(path);
    } else if (Array.isArray(v)) {
      v.forEach((item, i) => walk(item, `${path}[${i}]`));
    } else if (v !== null && typeof v === "object") {
      for (const [k, item] of Object.entries(v)) walk(item, path ? `${path}.${k}` : k);
    }
  };
  walk(value, base);
  return found;
}
