import { readdirSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");

export interface FoundDoc {
  file: string;
  path: string;
  doc: unknown;
}

/** Every object with `type === "doc"` in every pilot question, at any depth. */
export function pilotDocs(): FoundDoc[] {
  const dir = resolve(root, "content/pilot");
  const found: FoundDoc[] = [];
  for (const file of readdirSync(dir).filter((f) => f.endsWith(".json")).sort()) {
    const data = JSON.parse(readFileSync(resolve(dir, file), "utf8")) as unknown;
    const walk = (v: unknown, path: string): void => {
      if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${path}[${i}]`));
      else if (v && typeof v === "object") {
        if ((v as { type?: unknown }).type === "doc") found.push({ file, path, doc: v });
        else for (const [k, x] of Object.entries(v)) walk(x, `${path}.${k}`);
      }
    };
    walk(data, "");
  }
  return found;
}

export function pilotQuestionCount(): number {
  const dir = resolve(root, "content/pilot");
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .reduce((n, f) => n + (JSON.parse(readFileSync(resolve(dir, f), "utf8")) as { questions: unknown[] }).questions.length, 0);
}
